#!/bin/sh

cd web && \
uvicorn main:app --reload
