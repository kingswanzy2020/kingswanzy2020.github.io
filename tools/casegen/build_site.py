"""Build the whole site: generated case studies, the five hand-built ones restyled,
prev/next links on every case study, and the landing page."""
import os, re, html
import gen

SITE = gen.SITE
RAW = gen.RAW
NW = "https://learn.nextwork.org/thoughtful_white_zany_vampire/uploads/"

GROUPS = [("k8s", "Kubernetes &amp; GitOps"), ("cicd", "CI/CD"), ("iac", "Infrastructure as Code"),
          ("aws", "AWS Cloud"), ("ai", "AI &times; DevOps"), ("obs", "Observability"), ("net", "Networking")]
GROUP_SHORT = {"k8s": "Kubernetes", "cicd": "CI/CD", "iac": "IaC", "aws": "AWS", "ai": "AI &times; Ops", "obs": "Observability", "net": "Networking"}

# The five hand-built case studies that predate the generator.
LEGACY = {
    "eks": dict(group="k8s", title="Production application on Amazon EKS", status="Decommissioned",
                desc="A three-tier app on a two-node cluster &mdash; DNS, TLS, storage and autoscaling all provisioned by controllers, not by hand."),
    "argocd-pipeline": dict(group="k8s", title="GitOps deployment pipeline with ArgoCD", status="Decommissioned",
                desc="A cluster that reverts manual changes within seconds &mdash; Git is the only way anything gets in."),
    "fastapi-react": dict(group="k8s", title="A FastAPI + React template, from compose to Kubernetes", status="Decommissioned",
                desc="Terraform, Ansible, one Helm chart and a pipeline around an existing app &mdash; then a broken release shipped on purpose, which never took traffic."),
    "terraform-gitops": dict(group="iac", title="Terraform GitOps pipeline on AWS", status="Decommissioned",
                desc="A five-module AWS stack where every change is a plan on PR, applied only on merge, authenticated via OIDC."),
    "delivery-scoreboard": dict(group="obs", title="DORA delivery scoreboard with DuckDB", status="Local script",
                desc="Four metrics computed in SQL; a fifth withheld until an AI classifier's labels pass an 18/20 accuracy gate."),
}

TAGS = {
    "eks": ["Amazon EKS", "Helm", "cert-manager", "IRSA", "HPA"],
    "argocd-pipeline": ["ArgoCD", "Kustomize", "Sealed Secrets", "Renovate"],
    "fastapi-react": ["Kubernetes", "Helm", "Terraform", "Ansible", "GitHub Actions"],
    "gitops-5g-core": ["ArgoCD", "Operators", "Open5GS", "Kustomize", "Prometheus"],
    "jenkins-argocd-gitops": ["Jenkins", "ArgoCD", "Terraform", "Docker"],
    "helm-cicd-monitoring": ["Helm", "Jenkins", "Prometheus", "Grafana"],
    "eks-cluster-launch": ["Amazon EKS", "eksctl", "CloudFormation", "RBAC"],
    "eks-backend-image": ["Docker", "Amazon ECR", "eksctl"],
    "jenkins-sonarqube": ["Jenkins", "SonarQube", "Maven", "Docker"],
    "aws-cicd-pipeline": ["CodePipeline", "CodeBuild", "CodeDeploy", "CloudFormation"],
    "github-actions-ci": ["GitHub Actions", "pytest", "Python"],
    "rag-semantic-ci": ["GitHub Actions", "RAG", "Semantic tests"],
    "ai-pr-review": ["GitHub Actions", "Gemini", "github-script"],
    "terraform-gitops": ["Terraform", "GitHub Actions", "OIDC", "AWS"],
    "terraform-s3": ["Terraform", "Amazon S3"],
    "serverless-lead-capture": ["Lambda", "API Gateway", "CloudFront", "DynamoDB", "SES"],
    "three-tier-serverless": ["CloudFront", "API Gateway", "Lambda", "DynamoDB"],
    "cross-account-ecr": ["Amazon ECR", "IAM", "Elastic Beanstalk"],
    "elastic-beanstalk-docker": ["Docker", "Elastic Beanstalk"],
    "iam-permissions-boundary": ["IAM", "Policy simulator", "AWS CLI"],
    "iam-tag-based-access": ["IAM", "ABAC", "EC2"],
    "aurora-web-app": ["Aurora MySQL", "EC2", "PHP"],
    "s3-static-website": ["Amazon S3", "Bucket policies"],
    "ai-incident-response": ["Fluent Bit", "Ollama", "Redis", "FastAPI"],
    "rag-api": ["FastAPI", "Chroma", "Docker", "Minikube"],
    "ai-security-scanner": ["Python", "Gemini", "AppSec"],
    "delivery-scoreboard": ["Python", "DuckDB", "SQL", "DORA"],
    "grafana-mcp": ["Grafana", "MCP", "PostgreSQL"],
    "nginx-gateway": ["NGINX", "Reverse proxy", "Caching"],
}

ORDER = {
    "k8s": ["fastapi-react", "eks", "gitops-5g-core", "argocd-pipeline", "jenkins-argocd-gitops", "helm-cicd-monitoring", "eks-cluster-launch", "eks-backend-image"],
    "cicd": ["jenkins-sonarqube", "aws-cicd-pipeline", "rag-semantic-ci", "ai-pr-review", "github-actions-ci"],
    "iac": ["terraform-gitops", "terraform-s3"],
    "aws": ["serverless-lead-capture", "iam-permissions-boundary", "three-tier-serverless", "cross-account-ecr", "iam-tag-based-access", "elastic-beanstalk-docker", "aurora-web-app", "s3-static-website"],
    "ai": ["ai-incident-response", "rag-api", "ai-security-scanner"],
    "obs": ["delivery-scoreboard", "grafana-mcp"],
    "net": ["nginx-gateway"],
}

FEATURED = [(s, f"assets/thumbs/{s}.jpg") for s in [
    "fastapi-react", "eks", "gitops-5g-core", "ai-incident-response",
    "terraform-gitops", "argocd-pipeline", "jenkins-argocd-gitops", "delivery-scoreboard"]]


PROOF = {
    "fastapi-react": "A broken release never took traffic &middot; HPA 2 &rarr; 4 &rarr; 6 in about a minute",
    "eks": "TLS, DNS and ALB with zero console clicks &middot; HPA 2 &rarr; 3 at 60% CPU",
    "gitops-5g-core": "New network slice: commit &rarr; synced in ~2 minutes",
    "ai-incident-response": "One GitHub issue per error signature, not per log line",
    "terraform-gitops": "Zero stored AWS keys &mdash; OIDC only, apply only on merge",
    "argocd-pipeline": "Manual drift reverted by self-heal within seconds",
    "jenkins-argocd-gitops": "~2 min from manifest commit to 2/2 pods running",
    "delivery-scoreboard": "AI-derived metric gated at &ge;18/20 &mdash; released at 20/20",
}

TOOLBOX = [
    ("Containers &amp; orchestration", ["Kubernetes (CKA)", "EKS", "Helm", "Kustomize", "ArgoCD", "Operators", "Docker"]),
    ("Infrastructure as code", ["Terraform", "Ansible", "CloudFormation", "Checkov", "TFLint"]),
    ("CI/CD", ["GitHub Actions", "Jenkins", "CodePipeline", "SonarQube", "Trivy", "Renovate"]),
    ("Observability", ["Prometheus", "Grafana", "CloudWatch", "Fluent Bit", "DuckDB"]),
    ("AWS", ["EKS", "EC2", "VPC", "IAM", "S3", "RDS / Aurora", "Lambda", "Route 53", "CloudFront"]),
    ("Security", ["IAM least privilege", "OIDC federation", "RBAC", "Sealed Secrets", "permissions boundaries"]),
    ("AI for operations", ["Ollama", "Gemini API", "RAG", "MCP", "LLM output gating"]),
    ("Languages &amp; networking", ["Python", "Bash", "Linux", "NGINX", "TCP/IP", "OSPF / BGP"]),
]


def catalog():
    pages = {P["slug"]: P for P in gen.load_pages()}
    cat = {}
    for slug, P in pages.items():
        c = P["card"]
        cat[slug] = dict(group=c["group"], title=c["title"], desc=c["desc"], status=c["status"], page=P)
    for slug, c in LEGACY.items():
        cat[slug] = dict(c, page=None)
    ordered = [s for g, _ in GROUPS for s in ORDER[g]]
    assert sorted(ordered) == sorted(cat), set(ordered) ^ set(cat)
    return cat, ordered


def next_nav(cat, ordered, slug):
    i = ordered.index(slug)
    prev_s, next_s = ordered[i - 1], ordered[(i + 1) % len(ordered)]
    return f"""  <nav class="next" aria-label="More case studies">
    <a href="../{prev_s}/"><small>&larr; Previous</small>{cat[prev_s]['title']}</a>
    <a class="r" href="../{next_s}/"><small>Next &rarr;</small>{cat[next_s]['title']}</a>
  </nav>
"""


def restyle_legacy(slug, nav):
    path = os.path.join(SITE, slug, "index.html")
    s = open(path).read()
    s = re.sub(r'<link rel="preconnect".*?</style>', lambda m: gen.HEAD_LINKS, s, count=1, flags=re.S)
    s = re.sub(r'<meta name="theme-color".*?<link rel="stylesheet" href="\.\./assets/site\.css">', lambda m: gen.HEAD_LINKS, s, count=1, flags=re.S)
    s = s.replace("<body>", '<body class="case">', 1)
    s = re.sub(r'<div class="bar">.*?\n</div>\n', lambda m: gen.BAR, s, count=1, flags=re.S)
    s = re.sub(r'  <nav class="next".*?</nav>\n', "", s, flags=re.S)
    s = s.replace('  <footer class="col">', nav + '  <footer class="col">', 1)
    open(path, "w").write(s)


# ---------------------------------------------------------------- landing
ICON = {
    "github": '<svg viewBox="0 0 16 16" fill="currentColor" aria-hidden="true"><path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"/></svg>',
    "linkedin": '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M20.45 20.45h-3.55v-5.57c0-1.33-.02-3.04-1.85-3.04-1.86 0-2.14 1.45-2.14 2.94v5.67H9.36V9h3.41v1.56h.05c.48-.9 1.64-1.85 3.37-1.85 3.6 0 4.27 2.37 4.27 5.46v6.28zM5.34 7.43a2.06 2.06 0 110-4.12 2.06 2.06 0 010 4.12zM7.12 20.45H3.56V9h3.56v11.45zM22.22 0H1.77C.79 0 0 .77 0 1.73v20.54C0 23.23.79 24 1.77 24h20.45c.98 0 1.78-.77 1.78-1.73V1.73C24 .77 23.2 0 22.22 0z"/></svg>',
    "mail": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3.5 6l8.5 7 8.5-7"/></svg>',
    "folder": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 7a2 2 0 012-2h4l2 2h8a2 2 0 012 2v8a2 2 0 01-2 2H5a2 2 0 01-2-2z"/></svg>',
}

EXPERIENCE = [
    dict(when="2025 &mdash; Now", title="Freelance DevOps, Platform &amp; SRE Engineer", co="Independent",
         sub="Remote &middot; Daejeon, South Korea",
         body="<p>Taking on SRE, platform and DevOps-AI work: Kubernetes platforms and GitOps delivery, Terraform on AWS, observability with Prometheus and Grafana, and LLM-assisted tooling for incident response and code review. Alongside client work I build in public &mdash; every project in the archive below is written up with what I measured, what I only observed, and what broke.</p>",
         tags=["Kubernetes", "ArgoCD", "Terraform", "AWS", "Prometheus", "Python"]),
    dict(when="2023 &mdash; 2025", title="Graduate Research Assistant", co="Hanbat National University",
         sub="Intelligent Antenna &amp; Radar Sensing Lab &middot; Daejeon, South Korea",
         body="<ul><li>Designed and optimised complex telecommunications systems with systematic, data-driven methods.</li><li>Diagnosed failures across RF hardware, instrumentation and software toolchains &mdash; isolating one layer at a time, the same method I use on distributed systems.</li><li>Worked with international, multidisciplinary teams across time zones; wrote the documentation and presented findings to faculty and external stakeholders.</li></ul>",
         tags=["Research", "Instrumentation", "Debugging", "Technical writing"]),
    dict(when="2020 &mdash; 2021", title="Network Systems Engineer", co="K-NET Limited",
         sub="Telecommunications infrastructure &middot; Accra, Ghana",
         body="<ul><li>Deployed and maintained production network infrastructure for enterprise clients across distributed sites, sustaining 99% service availability.</li><li>Managed infrastructure releases and configuration changes; carried on-call production support with root-cause analysis &mdash; an SRE rotation before I knew to call it that.</li><li>Configured IP addressing, subnetting, VLAN segmentation and OSPF/BGP routing, and integrated IoT devices for remote fuel-level monitoring across sites.</li></ul>",
         tags=["OSPF / BGP", "VLANs", "On-call", "IoT"]),
    dict(when="2019", title="IT Technician (Internship)", co="The Multimedia Group Ltd.",
         sub="Accra, Ghana",
         body="<p>Deployed and configured workstations, operating systems and network devices across office and retail sites; owned Tier 1&ndash;2 escalations and the full PC lifecycle through a hardware refresh, under peak business-hour pressure.</p>",
         tags=["Endpoints", "Networking", "Support"]),
]

CERTS = [
    dict(seal="CKA", title="Certified Kubernetes Administrator", by="Cloud Native Computing Foundation",
         url="https://www.credly.com/badges/8717d9d9-a9ab-422e-a463-54a24d626c1a/public_url"),
    dict(seal="SAA", title="AWS Certified Solutions Architect &ndash; Associate", by="Amazon Web Services",
         url="https://www.credly.com/badges/c33ee367-fc26-4d1a-acff-ef4eb7feb159/public_url"),
    dict(seal="CCP", title="AWS Certified Cloud Practitioner", by="Amazon Web Services",
         url="https://www.credly.com/badges/ac46a454-8d43-4b0a-ba08-f70c79a1c53b/public_url"),
    dict(seal="IBM", title="Introduction to DevOps &middot; Linux Commands &amp; Shell Scripting", by="IBM", url=None),
]


def pills(tags):
    return '<ul class="pills">' + "".join(f"<li>{t}</li>" for t in tags) + "</ul>"


def landing(cat, ordered):
    exp = []
    for e in EXPERIENCE:
        exp.append(f"""        <li class="item">
          <div class="when">{e['when']}</div>
          <div>
            <h3>{e['title']} <span class="co">&middot; {e['co']}</span></h3>
            <p class="sub">{e['sub']}</p>
            {e['body']}
            {pills(e['tags'])}
          </div>
        </li>""")
    feat = []
    for slug, thumb in FEATURED:
        c = cat[slug]
        feat.append(f"""        <li class="item has-thumb">
          <img class="thumb" loading="lazy" src="{thumb}" alt="" width="150" height="94">
          <div>
            <p class="eyebrow-s">{GROUP_SHORT[c['group']]} &middot; {c['status']}</p>
            <h3><a href="{slug}/">{c['title']}<span class="arr" aria-hidden="true">&#8599;</span></a></h3>
            <p>{c['desc']}</p>
            <p class="proof">{PROOF[slug]}</p>
            {pills(TAGS[slug])}
          </div>
        </li>""")
    rows = []
    for g, label in GROUPS:
        for slug in ORDER[g]:
            c = cat[slug]
            rows.append(f"""          <tr>
            <td class="dom">{GROUP_SHORT[g]}</td>
            <td class="ttl"><a href="{slug}/">{c['title']}</a><small>{c['desc']}</small></td>
            <td class="col-stack">{pills(TAGS[slug][:3])}</td>
            <td class="st col-st">{c['status']}</td>
          </tr>""")
    certs = []
    for c in CERTS:
        link = f'<a class="verify" href="{c["url"]}">Verify on Credly &#8599;</a>' if c["url"] else ""
        certs.append(f"""        <div class="cert{'' if c['url'] else ' plain'}">
          <span class="seal">{c['seal']}</span>
          <div><h3>{c['title']}</h3><p>{c['by']}</p>{link}</div>
        </div>""")
    tools = "\n".join(f'        <div><h3>{g}</h3>{pills(t)}</div>' for g, t in TOOLBOX)
    n = len(ordered)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Ahmed Tetteh &mdash; DevOps, Platform &amp; SRE Engineer</title>
<meta name="description" content="Ahmed Tetteh is a freelance DevOps, platform and SRE engineer (CKA, AWS SAA) in Daejeon, South Korea. {n} case studies in Kubernetes, GitOps, Terraform, AWS, observability and AI for operations, each separating what was measured from what was designed.">
<meta property="og:title" content="Ahmed Tetteh &mdash; DevOps, Platform &amp; SRE Engineer">
<meta property="og:description" content="Kubernetes, GitOps, Terraform, AWS and AI-assisted operations &mdash; {n} case studies, written up with what was measured and what broke.">
<meta property="og:type" content="website">
<meta property="og:url" content="https://kingswanzy2020.github.io/">
<meta name="theme-color" content="#0b1220">
<link rel="icon" href="assets/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap">
<link rel="stylesheet" href="assets/site.css">
</head>
<body>
<a class="skip" href="#content">Skip to content</a>
<div class="layout">

  <header class="side">
    <div>
      <span class="avatar lg" role="img" aria-label="Photo of Ahmed Tetteh">AT</span>
      <h1>Ahmed Tetteh</h1>
      <p class="role">DevOps, Platform &amp; SRE Engineer</p>
      <p class="tag">I build infrastructure that's automated, observable and secure by default &mdash; and I write down what I actually proved.</p>
      <span class="pill-status"><i aria-hidden="true"></i>Freelancing &middot; open to roles</span>
      <div class="meta"><span>Daejeon, South Korea</span><span>Remote or relocation</span><span>CKA &middot; AWS SAA</span></div>
      <nav class="toc" aria-label="Sections">
        <ol>
          <li><a href="#about"><span class="l"></span>About</a></li>
          <li><a href="#experience"><span class="l"></span>Experience</a></li>
          <li><a href="#toolbox"><span class="l"></span>Toolbox</a></li>
          <li><a href="#work"><span class="l"></span>Selected work</a></li>
          <li><a href="#archive"><span class="l"></span>All {n} case studies</a></li>
          <li><a href="#certifications"><span class="l"></span>Certifications</a></li>
          <li><a href="#contact"><span class="l"></span>Contact</a></li>
        </ol>
      </nav>
    </div>
    <div class="social">
      <a href="https://github.com/kingswanzy2020" aria-label="GitHub">{ICON['github']}</a>
      <a href="https://www.linkedin.com/in/ahmed-tetteh-76a538126/" aria-label="LinkedIn">{ICON['linkedin']}</a>
      <a href="mailto:kingsleyswanzy@gmail.com" aria-label="Email">{ICON['mail']}</a>
      <a href="https://github.com/kingswanzy2020/Projects" aria-label="All projects on GitHub">{ICON['folder']}</a>
    </div>
  </header>

  <main class="main" id="content">

    <section id="about" class="about" aria-label="About">
      <h2 class="sec-h only-mobile">About</h2>
      <p>&#128075; Hi, I'm Ahmed &mdash; a DevOps and platform engineer based in Daejeon, South Korea. Right now I'm freelancing, taking on <strong>SRE, platform and DevOps-AI</strong> work: Kubernetes clusters, GitOps and Terraform pipelines on AWS, observability, and tooling that lets an LLM help during an incident without being trusted blindly.</p>
      <p>I came to this through networks. My first engineering job was keeping production network infrastructure up for enterprise clients in Ghana &mdash; releases, on-call and root-cause analysis, before I knew to call it SRE. Then I moved to Korea for an MSc in telecommunications and spent two years as a research assistant in a radar-sensing lab, where debugging RF hardware one layer at a time turned out to be excellent practice for debugging distributed systems.</p>
      <p>I'm a <a href="{CERTS[0]['url']}">Certified Kubernetes Administrator</a> and an <a href="{CERTS[1]['url']}">AWS Solutions Architect &ndash; Associate</a>. Every project on this page is written up the same way: what I built, what I <em>measured</em>, what I only <em>observed</em>, what holds only <em>by design</em> &mdash; and what broke. I'd rather show you the 403s than pretend they didn't happen.</p>
      <p>I'm open to freelance engagements and full-time roles, remote or with relocation.</p>
    </section>

    <section id="experience" aria-label="Experience">
      <h2 class="sec-h">Experience</h2>
      <ol class="list">
{chr(10).join(exp)}
      </ol>
      <ul class="edu" aria-label="Education" style="margin-top:28px">
        <li><span class="when">2025</span><span><b>MSc, Electrical Engineering (Telecommunications)</b>Hanbat National University, Daejeon, South Korea</span></li>
        <li><span class="when">2020</span><span><b>BSc, Telecommunication Engineering</b>Kwame Nkrumah University of Science and Technology, Kumasi, Ghana</span></li>
      </ul>
    </section>

    <section id="toolbox" aria-label="Toolbox">
      <h2 class="sec-h">Toolbox</h2>
      <div class="toolbox">
{tools}
      </div>
    </section>

    <section id="work" aria-label="Selected work">
      <h2 class="sec-h">Selected work</h2>
      <ol class="list">
{chr(10).join(feat)}
      </ol>
      <a class="more" href="#archive">See all {n} case studies <span aria-hidden="true">&rarr;</span></a>
    </section>

    <section id="archive" aria-label="All case studies">
      <h2 class="sec-h">All {n} case studies</h2>
      <p>Each one has an architecture diagram, a wiring table, a ledger of what was measured versus assumed, screenshots, and the failures worth keeping. The code lives in <a href="https://github.com/kingswanzy2020/Projects">the Projects repo</a> and the source repos it links to.</p>
      <table class="archive">
        <thead><tr><th>Area</th><th>Case study</th><th class="col-stack">Built with</th><th class="col-st">Status</th></tr></thead>
        <tbody>
{chr(10).join(rows)}
        </tbody>
      </table>
    </section>

    <section id="certifications" aria-label="Certifications">
      <h2 class="sec-h">Certifications</h2>
      <div class="certs">
{chr(10).join(certs)}
      </div>
    </section>

    <section id="contact" class="contact" aria-label="Contact">
      <h2 class="sec-h">Contact</h2>
      <p>If you need a Kubernetes platform stood up properly, a delivery pipeline untangled, or someone to make an on-call rotation quieter, I'd like to hear about it. The fastest way to reach me is email.</p>
      <a class="btn" href="mailto:kingsleyswanzy@gmail.com">kingsleyswanzy@gmail.com</a>
    </section>

    <p class="foot">Hand-written HTML and CSS, hosted on GitHub Pages &mdash; no JavaScript, no framework, no build step for the pages themselves. Layout inspired by <a href="https://brittanychiang.com">Brittany Chiang</a>.</p>
  </main>

</div>
</body>
</html>
"""


if __name__ == "__main__":
    cat, ordered = catalog()
    for slug in ordered:
        P = cat[slug]["page"]
        nav = next_nav(cat, ordered, slug)
        if P is None:
            restyle_legacy(slug, nav)
        else:
            P["_next"] = nav
            with open(os.path.join(SITE, slug, "index.html"), "w") as fh:
                fh.write(gen.page(P))
    with open(os.path.join(SITE, "index.html"), "w") as fh:
        fh.write(landing(cat, ordered))
    print("built", len(ordered), "case studies + landing")
