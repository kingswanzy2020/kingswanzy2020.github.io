#!/usr/bin/env bash
# Drop real vendor logos into the architecture diagram.
#
# The page ships with neutral geometric glyphs. Each icon slot in the SVG is
# marked <!--ICON:name--> followed by a commented-out <image> tag pointing at
# assets/icons/<name>.svg. Put the real SVGs there, run this, and the slots
# switch over. Nothing else in the page changes.
#
#   usage:  ./add-real-icons.sh path/to/eks-production-app.html
#
# Files to place in assets/icons/ (keep these exact names):
#   route53.svg  alb.svg  ebs.svg          -> AWS Architecture Icons
#                                             https://aws.amazon.com/architecture/icons/
#   kubernetes.svg                          -> https://github.com/cncf/artwork  (CNCF)
#   nginx.svg postgresql.svg                -> each project's own press/brand page
#   cert-manager.svg external-dns.svg
#   aws-load-balancer-controller.svg
#   metrics-server.svg grafana.svg
#   httpbin.svg browser.svg                 -> any neutral icon set you like
#
# Check each project's trademark terms before publishing. AWS's icon licence
# permits use in architecture diagrams like this one.
set -euo pipefail
f="${1:?usage: add-real-icons.sh <html file>}"
cp "$f" "$f.bak"
perl -0pi -e 's/<!--(<image href="assets\/icons\/[^"]+\.svg"[^>]*\/>)-->/$1/g' "$f"
echo "enabled $(grep -o 'image href="assets/icons' "$f" | wc -l) icon slots in $f (backup: $f.bak)"
