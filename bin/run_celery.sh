#!/usr/bin/env bash
cd automappa
su -m automappa -c "celery --app=tasks worker --loglevel INFO"
