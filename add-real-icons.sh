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
#           ./add-real-icons.sh terraform-gitops/index.html
#           ./add-real-icons.sh argocd-pipeline/index.html
#           ./add-real-icons.sh delivery-scoreboard/index.html
#
# The same icon file is reused across pages where the same tool appears in
# more than one diagram (kubernetes.svg, github.svg, engineer.svg) — drop it
# in once and every page picks it up.
#
# Files to place in assets/icons/ (keep these exact names):
#   route53.svg  alb.svg  ebs.svg  ec2.svg     -> AWS Architecture Icons
#   iam.svg  s3.svg  rds.svg  dynamodb.svg        https://aws.amazon.com/architecture/icons/
#   vpc.svg
#   kubernetes.svg                             -> https://github.com/cncf/artwork  (CNCF)
#   argocd.svg                                 -> https://argo-cd.readthedocs.io (brand assets)
#   terraform.svg  github-actions.svg          -> HashiCorp / GitHub brand assets
#   nginx.svg  postgresql.svg  duckdb.svg      -> each project's own press/brand page
#   cert-manager.svg  external-dns.svg
#   sealed-secrets.svg  renovate.svg
#   aws-load-balancer-controller.svg
#   metrics-server.svg  grafana.svg
#   github.svg                                 -> GitHub logo/brand assets
#   httpbin.svg  browser.svg  engineer.svg     -> any neutral icon set you like
#   presync-hook.svg  workload.svg  corpus.svg
#   sql.svg  assert.svg  clock.svg  ai.svg
#   gate.svg  join.svg  html.svg
#
# Check each project's trademark terms before publishing. AWS's icon licence
# permits use in architecture diagrams like this one.
set -euo pipefail
f="${1:?usage: add-real-icons.sh <html file>}"
cp "$f" "$f.bak"
perl -0pi -e 's/<!--(<image href="(?:\.\.\/)?assets\/icons\/[^"]+\.svg"[^>]*\/>)-->/$1/g' "$f"
echo "enabled $(grep -o 'image href="[^"]*assets/icons' "$f" | wc -l) icon slots in $f (backup: $f.bak)"
