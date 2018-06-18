#!/bin/bash
echo Starting Daphne
exec daphne -b 0.0.0.0 -p 3000 mysite.asgi:application
