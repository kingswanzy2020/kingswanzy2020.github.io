#!/usr/bin/env bash
# Drop real vendor logos into an architecture diagram.
#
# Each page ships with neutral geometric glyphs. Every icon slot in its SVG is
# marked <!--ICON:name--> followed by a commented-out <image> tag pointing at
# assets/icons/<name>.svg (one directory up from each case-study page). Put
# the real SVGs there, run this against each page, and the slots switch over.
# Nothing else in the page changes.
#
#   usage:  ./add-real-icons.sh eks/index.html
#           for f in */index.html; do ./add-real-icons.sh "$f"; done
#
# The same icon file is reused wherever the same tool appears in more than one
# diagram (kubernetes.svg, github.svg, engineer.svg, ...) — drop it in once
# and every page picks it up.
#
# Files to place in assets/icons/ (keep these exact names):
#   AWS Architecture Icons  https://aws.amazon.com/architecture/icons/
#     acm alb api-gateway aurora cloudformation cloudfront cloudwatch
#     codeartifact codebuild codedeploy codepipeline dynamodb ebs ec2 ecr eks
#     elastic-beanstalk iam lambda rds route53 s3 ses vpc
#     aws-load-balancer-controller
#   CNCF artwork            https://github.com/cncf/artwork
#     kubernetes helm prometheus fluent-bit operator
#   Each project's own brand page
#     argocd cert-manager external-dns sealed-secrets renovate metrics-server
#     grafana terraform github github-actions jenkins sonarqube maven junit
#     pytest python fastapi flask docker docker-hub nginx postgresql mysql php
#     redis celery duckdb chroma ollama open5gs slack mcp
#   Any neutral icon set
#     ai alert assert browser clock corpus doc engineer gate html httpbin
#     ingress join json presync-hook secrets sql terminal workload zip
#
# Check each project's trademark terms before publishing. AWS's icon licence
# permits use in architecture diagrams like this one.
set -euo pipefail
f="${1:?usage: add-real-icons.sh <html file>}"
cp "$f" "$f.bak"
perl -0pi -e 's/<!--(<image href="(?:\.\.\/)?assets\/icons\/[^"]+\.svg"[^>]*\/>)-->/$1/g' "$f"
echo "enabled $(grep -o 'image href="[^"]*assets/icons' "$f" | wc -l) icon slots in $f (backup: $f.bak)"
