#!/bin/sh
cd automappa
su -m automappa -c "celery -A tasks worker --loglevel INFO"  
