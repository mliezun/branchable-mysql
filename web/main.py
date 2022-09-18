import datetime
import itertools
import logging
import uuid
from typing import List

import sh
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from peewee import (CharField, DateTimeField, ForeignKeyField, IntegerField,
                    Model, SqliteDatabase, UUIDField)
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)

app = FastAPI()
sqlite_db = SqliteDatabase("app.db")


class DBBaseModel(Model):
    """A base model that will use our Sqlite database"""
    id = UUIDField(primary_key=True, default=uuid.uuid4)
    created = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = sqlite_db


class Layer(DBBaseModel):
    bottom_layer = ForeignKeyField("self", null=True)
    
class Branch(DBBaseModel):
    branch_name = CharField(unique=True)
    port = IntegerField(unique=True)
    layer = ForeignKeyField(Layer, default=Layer.create)
    
class CreateBranch(BaseModel):
    branch_name: str
    base_branch: str
    port: int | None
    
class BranchModel(BaseModel):
    branch_name: str
    
class APIMessage(BaseModel):
    message: str


BASE_PORT = 33061
COUNTER = itertools.count()
def get_port():
    return  BASE_PORT + next(COUNTER)


def start_mysqld(layer: str, port: int):
    return sh.mysqld(
        f"--defaults-file=/app/mysql/{layer}/conf/my.cnf",
        f"--datadir=/app/mysql/{layer}/data/",
        f"--pid-file=/app/mysql/{layer}/var/mysqld.pid",
        f"--socket=/app/mysql/{layer}/var/mysqld.sock",
        f"--secure-file-priv=/app/mysql/{layer}/var/lib/mysql-files",
        f"--port={port}",
        f"--log-error=/app/mysql/{layer}/logs/error.log",
        f"--log-bin=/app/mysql/{layer}/var/mysql-bin.log",
        f"--slow-query-log-file=/app/mysql/{layer}/logs/slow_query.log",
        f"--general-log-file=/app/mysql/{layer}/logs/query.log",
        f"--user=mysql",
        f"--bind-address=127.0.0.1",
        _bg=True,
        _out=logging.info,
        _err=logging.warn,
    )


def mount_layer(bottom_layers: List[str], new_layer: str):
    sh.mkdir(
        "-p",
        f"/app/layers/{new_layer}",
        _out=logging.info,
        _err=logging.warn,
    )
    sh.mkdir(
        "-p",
        f"/app/tmp/{new_layer}",
        _out=logging.info,
        _err=logging.warn,
    )
    sh.mkdir(
        "-p",
        f"/app/mysql/{new_layer}",
        _out=logging.info,
        _err=logging.warn,
    )
    lowerdir = ':'.join([f"/app/layers/{bottom_layer}" for bottom_layer in bottom_layers] + ["/app/layers/base"])
    sh.fuse_overlayfs(
        "-o",
        f"lowerdir={lowerdir},upperdir=/app/layers/{new_layer},workdir=/app/tmp/{new_layer}",
        "overlay",
        f"/app/mysql/{new_layer}",
        _out=logging.info,
        _err=logging.warn,
    )
    
def umount_layer(layer):
    sh.umount(
        f"/app/mysql/{layer}",
        _out=logging.info,
        _err=logging.warn,
    )


processes = {}


@app.post("/create-branch", response_model=CreateBranch, responses={404: {"model": APIMessage}})
def create_branch(branch: CreateBranch):
    if not Branch.filter(branch_name=branch.base_branch).exists():
        return JSONResponse(status_code=404, content={"message": "Base branch not found"})
    
    
    base_branch = Branch.get(branch_name=branch.base_branch)
    bottom_layer = str(base_branch.layer.id)
    base_proc = processes[branch.base_branch]
    del processes[branch.base_branch]
    base_proc.terminate()
    base_proc.wait()
    logging.info("Umounted layer")
    
    base_new_layer = Layer.create(bottom_layer=bottom_layer)
    layer = str(base_new_layer.id)
    previous_layers = []
    l = base_new_layer.bottom_layer
    while l:
        previous_layers.append(str(l.id))
        l = l.bottom_layer
    mount_layer(previous_layers, layer)
    processes[branch.base_branch] = start_mysqld(layer, base_branch.port)
    base_branch.layer = layer
    base_branch.save()
    
    new_layer = Layer.create(bottom_layer=bottom_layer)
    
    port = get_port()
    new_branch = Branch.create(branch_name=branch.branch_name, layer=new_layer, port=port)
    
    layer = str(new_branch.layer.id)
    mount_layer(previous_layers, layer)
    processes[branch.branch_name] = start_mysqld(layer, port)
    
    branch.port = port
    return branch

@app.delete("/delete-branch", response_model=BranchModel, responses={404: {"model": APIMessage}})
def delete_branch(branch: BranchModel):
    if not Branch.filter(branch_name=branch.branch_name).exists():
        return JSONResponse(status_code=404, content={"message": "Branch not found"})
    
    if branch.branch_name == "base":
        return JSONResponse(status_code=400, content={"message": "Cannot delete base branch"})
    
    Branch.get(Branch.branch_name == branch.branch_name).delete_instance()
    
    proc = processes[branch.branch_name]
    del processes[branch.branch_name]
    proc.terminate()
    proc.wait()
    
    return branch


@app.get("/list-branches", response_model=List[BranchModel], responses={404: {"model": APIMessage}})
def delete_branch():
    return [b for b in Branch.select().dicts()]


def startup():
    Layer.drop_table()
    Branch.drop_table()
    Layer.create_table()
    Branch.create_table()
    
    port = get_port()
    base_branch, _ = Branch.get_or_create(branch_name="base", port=port)
    layer = str(base_branch.layer.id)
    mount_layer([], layer)
    processes["base"] = start_mysqld(layer, port)
    
startup()
