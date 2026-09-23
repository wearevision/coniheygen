#!/bin/sh
# Genera public/index.html a partir de curso-heygen.html (que no trae <html>/<head>/<body>,
# porque también se publica como Artifact). Todo lo que está hasta el primer </style>
# va al <head>; el resto al <body>.
set -e
mkdir -p public
split=$(grep -n '</style>' curso-heygen.html | head -1 | cut -d: -f1)
{
  printf '<!doctype html>\n<html lang="es">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
  head -n "$split" curso-heygen.html
  printf '</head>\n<body>\n'
  tail -n +"$((split + 1))" curso-heygen.html
  printf '\n</body>\n</html>\n'
} > public/index.html
