# Icon registry

The only place to look up logos and icons. **Never Read this file whole:** look up with `grep -i '<brand>' icons/icons.md` and `ls icons/logos icons/ui | grep -i '<brand>'` before downloading anything.

- Listed: reuse `icons/<File>`; never download or copy it again. Not listed: download the **official** mark (brand/press kit, official repo, or the Wikimedia Commons copy of it) into `icons/logos/` (brands, tech) or `icons/ui/` (generic), append a row here (source, license, today's date), then use it.
- Never save icons in project folders. Every video that uses an icon adds the project to **Used in** (edit that one line).
- Names: lowercase-kebab-case, variant suffix if needed (`-wordmark`, `-lockup`, `-mono`, `-simple`, `-dark`, `-light`, `-alt`); plain `<brand>.svg` = preferred official mark; SVG first, else the largest PNG.
- Dates YYYY-MM-DD ("(est.)" = file mtime). License: what the source says, else "Trademark of owner (license not recorded)"; logos are used nominatively.
- Remotion: `public/icons` → this folder, so `staticFile('icons/logos/<file>')`.

| Name | File | Type | Source URL | License / brand guidelines | Downloaded | Used in |
|------|------|------|------------|----------------------------|------------|---------|
| a2a-black | `logos/a2a-black.svg` | SVG | https://github.com/a2aproject/A2A (docs/assets/a2a-logo-black.svg) | Trademark of owner (license not recorded) | 2026-11-04 | — |
| agui-dark | `logos/agui-dark.svg` | SVG | https://github.com/ag-ui-protocol/ag-ui (docs/logo/ag-ui-dark.svg) | Site favicon, owner trademark | 2026-11-04 | — |
| agui-favicon | `logos/agui-favicon.svg` | SVG | https://github.com/ag-ui-protocol/ag-ui (docs/favicon) | Site favicon, owner trademark | 2026-11-04 | — |
| agui-light | `logos/agui-light.svg` | SVG | https://github.com/ag-ui-protocol/ag-ui (docs/logo/ag-ui-light.svg) | Site favicon, owner trademark | 2026-11-04 | — |
| alpine | `logos/alpine.svg` | SVG | https://upload.wikimedia.org/wikipedia/commons/e/e6/Alpine_Linux.svg | Wikimedia Commons copy of official mark; trademark of owner | 2026-11-06 (est.) | — |
| amazon-ecr | `logos/amazon-ecr.svg` | SVG | https://d1.awsstatic.com/webteam/architecture-icons/q1-2025/Asset-Package_02072025.dee42cd0a6eaacc3da1ad9519579357fb546f803.zip | Trademark of owner (license not recorded) | 2026-11-06 (est.) | — |
| anthropic | `logos/anthropic.svg` | SVG | https://upload.wikimedia.org/wikipedia/commons/7/78/Anthropic_logo.svg | Wikimedia Commons copy of official mark; trademark of owner | 2026-11-05 | — |
| anthropic-symbol | `logos/anthropic-symbol.svg` | SVG | https://www.anthropic.com/press-kit | Official press kit | 2026-11-06 | system-design-of-ai/09-prompt-caching |
| anthropic-wordmark | `logos/anthropic-wordmark.svg` | SVG | https://www.anthropic.com/press-kit | Official press kit | 2026-11-06 | jensen-returns |
| apple | `logos/apple.svg` | SVG | https://upload.wikimedia.org/wikipedia/commons/f/fa/Apple_logo_black.svg | Wikimedia Commons copy of official mark; trademark of owner | 2026-10-28 | — |
| astral-badge | `logos/astral-badge.svg` | SVG | https://raw.githubusercontent.com/astral-sh/uv/main/assets/svg/Astral.svg | Repo asset ("Made by Astral" badge, not the plain mark); trademark of owner | 2026-11-19 | — |
| auth0 | `logos/auth0.jpg` | JPG | https://upload.wikimedia.org/wikipedia/commons/9/91/Auth0_logo_2026.jpg | Trademark of owner (license not recorded) | 2026-11-04 (est.) | — |
| auth0 | `logos/auth0.svg` | SVG | https://upload.wikimedia.org/wikipedia/commons/5/5b/Logo_de_Auth0.svg | Official brand page | 2026-11-06 (est.) | — |
| aws | `logos/aws.svg` | SVG | https://commons.wikimedia.org/wiki/File:Amazon_Web_Services_Logo.svg | Wikimedia Commons copy of official mark; trademark of owner | 2026-11-04 | — |
| buildah | `logos/buildah.svg` | SVG | https://raw.githubusercontent.com/containers/buildah/HEAD/logos/buildah-logo-source.svg | Repo asset; trademark of owner | 2026-11-06 (est.) | — |
| buildah-logomark | `logos/buildah-logomark.png` | PNG | https://raw.githubusercontent.com/containers/buildah/HEAD/logos/buildah-logo-source.svg | Repo asset; trademark of owner | 2026-11-06 (est.) | — |
| bullmq | `logos/bullmq.png` | PNG | https://github.com/taskforcesh/bullmq (README banner: https://user-images.githubusercontent.com/95200/143832033-32e868df-f3b0-4251-97fb-c64809a43d36.png) | Trademark of owner (license not recorded); official lockup from the project README | 2026-11-20 | system-design-of-ai/08-long-running-requests |
| cassandra | `logos/cassandra.png` | PNG | https://www.apache.org/logos/res/cassandra/default.png | Trademark of owner (license not recorded) | 2026-10-28 | — |
| chaicode | `logos/chaicode.svg` | SVG | https://chaicode.com/assets/favicon-dark-CYZX6cSs.svg | Site favicon, owner trademark | 2026-11-14 | — |
| claude | `logos/claude.svg` | SVG | https://upload.wikimedia.org/wikipedia/commons/b/b0/Claude_AI_symbol.svg | Trademark of owner (license not recorded) | 2026-11-04 (est.) | — |
| claude-logo | `logos/claude-logo.svg` | SVG | https://www.anthropic.com/press-kit ("Claude logos": Claude logo, Slate) | Official press kit | 2026-11-06 | system-design-of-ai/10-batch-inference, system-design-of-ai/09-prompt-caching |
| claude-spark | `logos/claude-spark.svg` | SVG | https://www.anthropic.com/press-kit ("Claude logos": Claude Spark, Clay) | Official press kit | 2026-11-06 | system-design-of-ai/07-provider-failover, system-design-of-ai/11-max-tokens-and-truncation |
| clerk-logotype-full-primary | `logos/clerk-logotype-full-primary.svg` | SVG | https://clerk.com/brand-assets | Trademark of owner (license not recorded) | 2026-10-31 | — |
| clerk-logotype-full-primary-light | `logos/clerk-logotype-full-primary-light.svg` | SVG | https://clerk.com/brand-assets | Trademark of owner (license not recorded) | 2026-10-31 | — |
| clerk-symbol-primary | `logos/clerk-symbol-primary.svg` | SVG | https://clerk.com/brand-assets | Trademark of owner (license not recorded) | 2026-10-31 | — |
| cloud-storage | `logos/cloud-storage.svg` | SVG | https://cloud.google.com/icons | Trademark of owner (license not recorded) | 2026-11-06 | — |
| cloudflare | `logos/cloudflare.svg` | SVG | https://commons.wikimedia.org/wiki/File:Cloudflare_Logo.svg | Wikimedia Commons copy of official mark; trademark of owner | 2026-11-03 | system-design-of-ai/08-long-running-requests |
| cognito | `logos/cognito.svg` | SVG | https://d1.awsstatic.com/onedam/marketing-channels/website/public/shared/architecture-icon-release/Icon-package_07312026.5846e92413caa21490223536cc97f1269e44fa92.zip | Official brand page | 2026-11-06 (est.) | — |
| containerd | `logos/containerd.svg` | SVG | https://raw.githubusercontent.com/cncf/artwork/main/projects/containerd/icon/color/containerd-icon-color.svg | Repo asset; trademark of owner | 2026-11-06 (est.) | — |
| containerd-horizontal | `logos/containerd-horizontal.svg` | SVG | https://raw.githubusercontent.com/cncf/artwork/main/projects/containerd/icon/color/containerd-icon-color.svg | Repo asset; trademark of owner | 2026-11-06 (est.) | — |
| copilotkit-dark | `logos/copilotkit-dark.svg` | SVG | https://github.com/CopilotKit/CopilotKit (assets/readme/logo-dark.svg) | Repo asset; trademark of CopilotKit | 2026-11-04 | — |
| copilotkit-light | `logos/copilotkit-light.svg` | SVG | https://github.com/CopilotKit/CopilotKit (assets/readme/logo-light.svg) | Repo asset; trademark of CopilotKit | 2026-11-04 | — |
| coreos | `logos/coreos.svg` | SVG | https://upload.wikimedia.org/wikipedia/commons/8/8c/CoreOS.svg | Wikimedia Commons copy of official mark; trademark of owner | 2026-11-06 (est.) | — |
| crewai | `logos/crewai.png` | PNG | https://github.com/crewAIInc/crewAI (docs/images/crewai_logo.png; no official SVG, 375x114) | Trademark of owner (license not recorded) | 2026-11-04 | — |
| crio | `logos/crio.svg` | SVG | https://raw.githubusercontent.com/cncf/artwork/main/projects/crio/icon/color/crio-icon-color.svg | Repo asset; trademark of owner | 2026-11-06 (est.) | — |
| crio-horizontal | `logos/crio-horizontal.svg` | SVG | https://raw.githubusercontent.com/cncf/artwork/main/projects/crio/icon/color/crio-icon-color.svg | Repo asset; trademark of owner | 2026-11-06 (est.) | — |
| crun | `logos/crun.svg` | SVG | https://raw.githubusercontent.com/containers/crun/HEAD/docs/crun.svg | Repo asset; trademark of owner | 2026-11-06 (est.) | — |
| cursor | `logos/cursor.svg` | SVG | https://cursor.com/marketing-static/favicon.svg | Site favicon, owner trademark | 2026-11-04 (est.) | — |
| cursor-cube-dark | `logos/cursor-cube-dark.svg` | SVG | https://cursor.com/brand (cursor-brand-assets.zip, General Logos) | Cursor brand page assets | 2026-11-06 | — |
| cursor-cube-light | `logos/cursor-cube-light.svg` | SVG | https://cursor.com/brand (cursor-brand-assets.zip, General Logos) | Cursor brand page assets | 2026-11-06 | — |
| cursor-lockup-dark | `logos/cursor-lockup-dark.svg` | SVG | https://cursor.com/brand (cursor-brand-assets.zip, General Logos) | Cursor brand page assets | 2026-11-06 | — |
| cursor-lockup-light | `logos/cursor-lockup-light.svg` | SVG | https://cursor.com/brand (cursor-brand-assets.zip, General Logos) | Cursor brand page assets | 2026-11-06 | — |
| cursor-simple | `logos/cursor-simple.svg` | SVG | https://cdn.jsdelivr.net/npm/simple-icons@16.36.0/icons/cursor.svg | Simple Icons (CC0 glyph); brand trademark of owner | 2026-11-14 | — |
| debezium | `logos/debezium.svg` | SVG | https://debezium.io/assets/images/color_black_debezium_type_600px.svg | Trademark of owner (license not recorded) | 2026-10-31 | — |
| docker | `logos/docker.svg` | SVG | https://cdn.simpleicons.org/docker/2496ED | CC0  | 2026-11-14 | — |
| docker-logo | `logos/docker-logo.svg` | SVG | https://www.docker.com/static/Docker-Logos-1.zip | Official press kit | 2026-11-06 (est.) | — |
| docker-mark | `logos/docker-mark.svg` | SVG | https://www.docker.com/static/Docker-Logos-1.zip | Official press kit | 2026-11-06 (est.) | — |
| docker-mark-white | `logos/docker-mark-white.svg` | SVG | https://www.docker.com/static/Docker-Logos-1.zip | Official press kit | 2026-11-06 (est.) | — |
| dotnet | `logos/dotnet.svg` | SVG | https://raw.githubusercontent.com/devicons/devicon/master/icons/dotnetcore/dotnetcore-original.svg | Repo asset; trademark of owner | 2026-11-06 (est.) | — |
| elasticsearch | `logos/elasticsearch.png` | PNG | https://static-www.elastic.co/…/logoparade-elasticsearch.png | Trademark of owner (license not recorded) | 2026-10-28 | — |
| entra | `logos/entra.svg` | SVG | https://upload.wikimedia.org/wikipedia/commons/8/8c/Microsoft_Entra_ID_color_icon.svg | Wikimedia Commons copy of official mark; trademark of owner | 2026-11-06 (est.) | — |
| express | `logos/express.svg` | SVG | https://raw.githubusercontent.com/expressjs/expressjs.com/HEAD/public/images/logos/logo-express-black.svg | Repo asset; trademark of owner | 2026-11-14 | system-design-of-ai/06-cancellation |
| facebook | `logos/facebook.svg` | SVG | https://upload.wikimedia.org/wikipedia/commons/b/b9/2023_Facebook_icon.svg | Wikimedia Commons copy of official mark; trademark of owner | 2026-10-28 | — |
| fastapi | `logos/fastapi.svg` | SVG | https://raw.githubusercontent.com/fastapi/fastapi/HEAD/docs/en/docs/img/logo-margin/logo-teal.svg | Repo asset; trademark of owner | 2026-11-06 (est.) | — |
| firebase | `logos/firebase.svg` | SVG | https://commons.wikimedia.org/wiki/File:Firebase_Logo_(No_wordmark | Wikimedia Commons copy of official mark; trademark of owner | 2026-11-03 | — |
| firebase-wordmark | `logos/firebase-wordmark.svg` | SVG | https://upload.wikimedia.org/wikipedia/commons/3/37/Firebase_Logo.svg | Wikimedia Commons copy of official mark; trademark of owner | 2026-11-06 (est.) | — |
| flutter | `logos/flutter.svg` | SVG | https://cdn.simpleicons.org/flutter/02569B | CC0 (mobile logo pick | 2026-11-14 | — |
| gemini | `logos/gemini.svg` | SVG | https://upload.wikimedia.org/wikipedia/commons/1/1d/Google_Gemini_icon_2025.svg | Wikimedia Commons copy of the official Gemini mark; trademark of Google | 2026-11-20 | system-design-of-ai/10-batch-inference, system-design-of-ai/11-max-tokens-and-truncation |
| git-icon | `logos/git-icon.svg` | SVG | https://git-scm.com/downloads/logos | CC BY 3.0 | 2026-11-06 | — |
| git-logo | `logos/git-logo.svg` | SVG | https://git-scm.com/downloads/logos | CC BY 3.0 | 2026-11-06 | — |
| github | `logos/github.svg` | SVG | https://commons.wikimedia.org/wiki/File:GitHub_Invertocat_Logo.svg | Wikimedia Commons copy of official mark; trademark of owner | 2026-11-03 | — |
| github-lockup | `logos/github-lockup.svg` | SVG | https://brand.github.com/GitHub_Logos.zip | Official brand toolkit | 2026-11-06 | — |
| github-mark | `logos/github-mark.svg` | SVG | https://brand.github.com/GitHub_Logos.zip | Official brand toolkit | 2026-11-06 | system-design-of-ai/06-cancellation |
| github-octicon | `logos/github-octicon.svg` | SVG | https://raw.githubusercontent.com/primer/octicons/HEAD/icons/mark-github-24.svg | Repo asset; trademark of owner | 2026-11-06 (est.) | — |
| gmail | `logos/gmail.svg` | SVG | https://upload.wikimedia.org/wikipedia/commons/8/8f/Gmail_icon_ | Trademark of owner (license not recorded) | 2026-11-04 (est.) | — |
| go | `logos/go.svg` | SVG | https://upload.wikimedia.org/wikipedia/commons/5/5c/Okta_logo.svg | Official press kit | 2026-11-06 (est.) | — |
| google | `logos/google.svg` | SVG | https://commons.wikimedia.org/wiki/File:Google_2015_logo.svg | Wikimedia Commons copy of official mark; trademark of owner | 2026-11-03 | — |
| google-g | `logos/google-g.svg` | SVG | https://upload.wikimedia.org/wikipedia/commons/c/c1/Google_%22G%22_logo.svg | Wikimedia Commons copy of official mark; trademark of owner | 2026-11-04 | — |
| graphify | `logos/graphify.svg` | SVG | https://graphify.com/assets/logo-icon.svg | Official site asset; trademark of owner | 2026-11-19 | — |
| graphql | `logos/graphql.svg` | SVG | https://raw.githubusercontent.com/graphql/graphql.github.io/source/public/img/logo.svg | Repo asset; trademark of owner | 2026-10-28 | — |
| heroku | `logos/heroku.svg` | SVG | https://commons.wikimedia.org/wiki/File:Heroku_logo.svg | Wikimedia Commons copy of official mark; trademark of owner | 2026-11-03 | system-design-of-ai/08-long-running-requests |
| instagram | `logos/instagram.svg` | SVG | https://upload.wikimedia.org/wikipedia/commons/e/e7/Instagram_logo_2016.svg | Wikimedia Commons copy of official mark; trademark of owner | 2026-10-28 | — |
| irdai | `logos/irdai.svg` | SVG | https://irdai.gov.in/o/irdai-theme/images/svg/logo/irdai-logo1.svg | Trademark of owner (license not recorded) | 2026-11-20 | system-design-of-ai/09-prompt-caching |
| javascript | `logos/javascript.svg` | SVG | https://cdn.simpleicons.org/javascript/F7DF1E | CC0 glyph  | 2026-11-14 | — |
| jira | `logos/jira.svg` | SVG | https://upload.wikimedia.org/wikipedia/commons/8/8a/Jira_Logo.svg | Trademark of owner (license not recorded) | 2026-11-04 (est.) | — |
| kafka | `logos/kafka.svg` | SVG | https://upload.wikimedia.org/wikipedia/commons/0/01/Apache_Kafka_logo.svg | Wikimedia Commons copy of official mark; trademark of owner | 2026-10-31 | — |
| kafka-simple | `logos/kafka-simple.svg` | SVG | https://cdn.simpleicons.org/apachekafka/231F20 | CC0  | 2026-11-14 | — |
| keycloak | `logos/keycloak.svg` | SVG | https://upload.wikimedia.org/wikipedia/commons/b/b4/Logo_of_Keycloak.svg | Trademark of owner (license not recorded) | 2026-11-04 (est.) | — |
| kilocode | `logos/kilocode.svg` | SVG | https://raw.githubusercontent.com/Kilo-Org/cloud/main/apps/web/public/kilo-v2.svg | Repo asset; trademark of owner | 2026-11-19 (est.) | — |
| kimi-lockup | `logos/kimi-lockup.svg` | SVG | https://www.kimi.com/en/resources/kimi-brand (kimi-logo-assets.zip, Lockup_Main/SVG/Lockup_Main_Light.svg) | Trademark of owner (license not recorded) | 2026-11-19 (est.) | — |
| kimi-logomark | `logos/kimi-logomark.svg` | SVG | https://www.kimi.com/en/resources/kimi-brand (kimi-logo-assets.zip, Logomark/SVG/Logomark_Dark.svg) | Official brand kit | 2026-11-19 (est.) | — |
| kubernetes | `logos/kubernetes.svg` | SVG | https://raw.githubusercontent.com/cncf/artwork/main/projects/kubernetes/icon/color/kubernetes-icon-color.svg | Repo asset; trademark of owner | 2026-11-06 (est.) | — |
| kubernetes-alt | `logos/kubernetes-alt.svg` | SVG | https://upload.wikimedia.org/wikipedia/commons/3/39/Kubernetes_logo_without_workmark.svg | Trademark of owner (license not recorded) | 2026-11-04 (est.) | — |
| kubernetes-word | `logos/kubernetes-word.svg` | SVG | https://upload.wikimedia.org/wikipedia/commons/3/39/Kubernetes_logo_without_workmark.svg | Trademark of owner (license not recorded) | 2026-11-04 (est.) | — |
| langchain-dark | `logos/langchain-dark.svg` | SVG | https://github.com/langchain-ai/langchain (.github/images/logo-dark.svg) | Repo asset; trademark of LangChain | 2026-11-04 | — |
| langchain-light | `logos/langchain-light.svg` | SVG | https://github.com/langchain-ai/langchain (.github/images/logo-light.svg) | Repo asset; trademark of LangChain | 2026-11-04 | — |
| linkedin | `logos/linkedin.svg` | SVG | https://upload.wikimedia.org/wikipedia/commons/a/aa/LinkedIn_2021.svg | Wikimedia Commons copy of official mark; trademark of owner | 2026-10-31 | — |
| linux-foundation | `logos/linux-foundation.svg` | SVG | https://upload.wikimedia.org/wikipedia/commons/f/fd/Linux_Foundation_logo_2013.svg | Wikimedia Commons copy of official mark; trademark of owner | 2026-11-06 (est.) | — |
| livejournal-icon | `logos/livejournal-icon.svg` | SVG | https://upload.wikimedia.org/wikipedia/commons/b/b3/LiveJournal_icon.svg | Trademark of owner (license not recorded) | 2026-11-04 (est.) | — |
| macos | `logos/macos.svg` | SVG | https://upload.wikimedia.org/wikipedia/commons/2/21/MacOS_wordmark_%282017%29.svg | Wikimedia Commons copy of official mark; trademark of owner | 2026-11-06 (est.) | — |
| masterji | `logos/masterji.png` | PNG | User-supplied (raw/masterji.png, 191x59 wordmark) | Supplied by the channel owner; owner trademark | 2026-11-14 | — |
| mcp-dark | `logos/mcp-dark.svg` | SVG | https://modelcontextprotocol.io/logo/{light,dark}.svg | Trademark of owner (license not recorded) | 2026-11-04 | — |
| mcp-light | `logos/mcp-light.svg` | SVG | https://modelcontextprotocol.io/logo/{light,dark}.svg | Trademark of owner (license not recorded) | 2026-11-04 | — |
| microsoft | `logos/microsoft.svg` | SVG | https://upload.wikimedia.org/wikipedia/commons/4/44/Microsoft_logo.svg | Wikimedia Commons copy of official mark; trademark of owner | 2026-11-04 | — |
| mongodb | `logos/mongodb.svg` | SVG | https://cdn.simpleicons.org/mongodb/47A248 | CC0  | 2026-11-14 | — |
| moonshot-wordmark-white | `logos/moonshot-wordmark-white.svg` | SVG | https://statics.kimi.ai/moonshot-ai/assets/static/moonshot-ai-wordmark.DeMGOuiG.svg | Trademark of owner (license not recorded) | 2026-11-19 (est.) | — |
| mozilla | `logos/mozilla.svg` | SVG | https://commons.wikimedia.org/wiki/File:Mozilla_2024_logo.svg | Wikimedia Commons copy of official mark; trademark of owner | 2026-11-03 | — |
| netlify | `logos/netlify.svg` | SVG | https://commons.wikimedia.org/wiki/File:Netlify_logo_(2 | Wikimedia Commons copy of official mark; trademark of owner | 2026-11-03 | — |
| nginx | `logos/nginx.svg` | SVG | https://commons.wikimedia.org/wiki/File:Nginx_logo.svg | Wikimedia Commons copy of official mark; trademark of owner | 2026-11-03 (est.) | system-design-of-ai/08-long-running-requests |
| nginx-simple | `logos/nginx-simple.svg` | SVG | https://cdn.simpleicons.org/nginx/009639 | CC0  | 2026-11-14 | — |
| nodejs | `logos/nodejs.svg` | SVG | https://upload.wikimedia.org/wikipedia/commons/d/d9/Node.js_logo.svg | Wikimedia Commons copy of official mark; trademark of owner | 2026-11-06 (est.) | system-design-of-ai/06-cancellation |
| nodejs-simple | `logos/nodejs-simple.svg` | SVG | https://cdn.simpleicons.org/nodedotjs/5FA04E | CC0  | 2026-11-14 | — |
| nodejs-wordmark | `logos/nodejs-wordmark.svg` | SVG | https://raw.githubusercontent.com/devicons/devicon/master/icons/nodejs/nodejs-original-wordmark.svg | Repo asset; trademark of owner | 2026-11-14 | — |
| oci | `logos/oci.svg` | SVG | https://raw.githubusercontent.com/opencontainers/artwork/HEAD/oci/icon/color/oci-icon-color.svg | Repo asset; trademark of owner | 2026-11-06 (est.) | — |
| oci-horizontal | `logos/oci-horizontal.svg` | SVG | https://raw.githubusercontent.com/opencontainers/artwork/HEAD/oci/icon/color/oci-icon-color.svg | Repo asset; trademark of owner | 2026-11-06 (est.) | — |
| okta | `logos/okta.svg` | SVG | https://upload.wikimedia.org/wikipedia/commons/8/83/Okta_logo_ | Trademark of owner (license not recorded) | 2026-11-04 (est.) | — |
| okta-alt | `logos/okta-alt.svg` | SVG | https://upload.wikimedia.org/wikipedia/commons/5/5c/Okta_logo.svg | Official press kit | 2026-11-06 (est.) | — |
| openai | `logos/openai.svg` | SVG | https://cdn.jsdelivr.net/npm/simple-icons@13.21.0/icons/openai.svg | mit | 2026-11-14 | system-design-of-ai/06-cancellation, system-design-of-ai/07-provider-failover, system-design-of-ai/08-long-running-requests, system-design-of-ai/10-batch-inference, system-design-of-ai/11-max-tokens-and-truncation, system-design-of-ai/09-prompt-caching, jensen-returns |
| openid | `logos/openid.svg` | SVG | https://upload.wikimedia.org/wikipedia/commons/c/c8/OpenID_logo.svg | Wikimedia Commons copy of official mark; trademark of owner | 2026-11-04 (est.) | — |
| pageindex-icon | `logos/pageindex-icon.svg` | SVG | https://pageindex.ai/static/brand/pageindex-favicon.svg | Site favicon, owner trademark | 2026-11-13 | — |
| pageindex-wordmark | `logos/pageindex-wordmark.svg` | SVG | https://pageindex.ai/static/brand/pageindex-wordmark.svg | Trademark of owner (license not recorded) | 2026-11-13 | — |
| php | `logos/php.svg` | SVG | https://raw.githubusercontent.com/devicons/devicon/master/icons/php/php-original.svg | Repo asset; trademark of owner | 2026-11-06 (est.) | — |
| pinecone-lockup | `logos/pinecone-lockup.svg` | SVG | https://www.pinecone.io/images/brand/pinecone-lockup-black.svg | Trademark of owner (license not recorded) | 2026-11-13 | — |
| pinecone-logomark | `logos/pinecone-logomark.svg` | SVG | https://www.pinecone.io/images/brand/pinecone-logomark-black.svg | Official brand page | 2026-11-13 | — |
| podman | `logos/podman.png` | PNG | https://raw.githubusercontent.com/containers/podman/HEAD/logo/podman-logo-source.svg | Repo asset; trademark of owner | 2026-11-06 (est.) | — |
| podman | `logos/podman.svg` | SVG | https://raw.githubusercontent.com/containers/podman/HEAD/logo/podman-logo-source.svg | Repo asset; trademark of owner | 2026-11-06 (est.) | — |
| postgresql | `logos/postgresql.svg` | SVG | https://wiki.postgresql.org/images/a/a4/PostgreSQL_logo.3colors.svg | Trademark of owner (license not recorded) | 2026-10-28 | system-design-of-ai/11-max-tokens-and-truncation |
| postgresql-simple | `logos/postgresql-simple.svg` | SVG | https://cdn.simpleicons.org/postgresql/4169E1 | CC0  | 2026-11-14 | — |
| python | `logos/python.svg` | SVG | https://raw.githubusercontent.com/devicons/devicon/master/icons/python/python-original.svg | Repo asset; trademark of owner | 2026-11-06 (est.) | — |
| rabbitmq | `logos/rabbitmq.svg` | SVG | https://www.rabbitmq.com/img/rabbitmq-logo.svg | Trademark of owner (license not recorded) | 2026-10-31 | — |
| ragas | `logos/ragas.png` | PNG | https://raw.githubusercontent.com/vibrantlabsai/ragas/main/docs/_static/imgs/logo.png | Repo asset; trademark of owner | 2026-11-05 | — |
| react | `logos/react.svg` | SVG | https://cdn.simpleicons.org/react/61DAFB | CC0  | 2026-11-14 | — |
| react-light | `logos/react-light.svg` | SVG | https://github.com/reactjs/react.dev (public/images/brand/logo_light.svg) | Trademark of owner (license not recorded) | 2026-11-04 | — |
| redis | `logos/redis.svg` | SVG | User-supplied classic Redis stacked-cubes logo (unmodified; redis.io has no direct download) | Trademark of owner (license not recorded) | 2026-10-28 | system-design-of-ai/08-long-running-requests, system-design-of-ai/09-prompt-caching |
| redis-simple | `logos/redis-simple.svg` | SVG | https://cdn.simpleicons.org/redis/FF4438 | CC0  | 2026-11-14 | — |
| redis-wordmark | `logos/redis-wordmark.svg` | SVG | https://commons.wikimedia.org/wiki/File:Redis_logo.svg | Public domain | 2024-04-18 | — |
| render | `logos/render.svg` | SVG | https://render.com/brand/render_1105076560.svg | Trademark of owner (license not recorded) | 2026-11-03 | — |
| replit | `logos/replit.svg` | SVG | https://cdn.jsdelivr.net/npm/simple-icons@13.21.0/icons/replit.svg | Simple Icons (CC0 glyph); brand trademark of owner | 2026-11-14 | — |
| runc | `logos/runc.svg` | SVG | https://raw.githubusercontent.com/opencontainers/artwork/HEAD/runc/icon/color/runc-icon-color.svg | Repo asset; trademark of owner | 2026-11-06 (est.) | — |
| runc-horizontal | `logos/runc-horizontal.svg` | SVG | https://raw.githubusercontent.com/opencontainers/artwork/HEAD/runc/icon/color/runc-icon-color.svg | Repo asset; trademark of owner | 2026-11-06 (est.) | — |
| rust | `logos/rust.svg` | SVG | https://raw.githubusercontent.com/devicons/devicon/master/icons/rust/rust-original.svg | Repo asset; trademark of owner | 2026-11-06 (est.) | — |
| samsung | `logos/samsung.svg` | SVG | https://cdn.jsdelivr.net/npm/simple-icons@16.36.0/icons/samsung.svg (path unmodified) | Simple Icons (CC0 glyph); brand trademark of owner | 2026-11-14 | — |
| spanner | `logos/spanner.svg` | SVG | https://cloud.google.com/icons | Trademark of owner (license not recorded) | 2026-11-06 | — |
| stackoverflow | `logos/stackoverflow.svg` | SVG | https://upload.wikimedia.org/wikipedia/commons/e/ef/Stack_Overflow_icon.svg | Wikimedia Commons copy of official mark; trademark of owner | 2026-11-06 (est.) | — |
| tessl-symbol | `logos/tessl-symbol.svg` | SVG | https://tessl.io/favicon.svg | Site favicon, owner trademark | 2026-11-19 (est.) | — |
| tessl-wordmark-white | `logos/tessl-wordmark-white.svg` | SVG | https://tessl.io/sanity/static/logo.svg | Trademark of owner (license not recorded) | 2026-11-19 (est.) | — |
| threads | `logos/threads.svg` | SVG | https://upload.wikimedia.org/wikipedia/commons/9/9d/Threads_%28app%29_logo.svg | Wikimedia Commons copy of official mark; trademark of owner | 2026-10-28 | — |
| tree-sitter | `logos/tree-sitter.png` | PNG | https://tree-sitter.github.io/tree-sitter/assets/images/tree-sitter-small.png | Repo asset; trademark of owner | 2026-11-19 | — |
| tux | `logos/tux.svg` | SVG | https://upload.wikimedia.org/wikipedia/commons/3/35/Tux.svg | Wikimedia Commons copy of official mark; trademark of owner | 2026-11-06 (est.) | — |
| uv | `logos/uv.svg` | SVG | https://raw.githubusercontent.com/astral-sh/uv/main/docs/assets/logo-letter.svg | Repo asset; trademark of owner | 2026-11-19 | — |
| vercel | `logos/vercel.svg` | SVG | https://commons.wikimedia.org/wiki/File:Vercel_logo_2025.svg | Wikimedia Commons copy of official mark; trademark of owner | 2026-11-03 | — |
| windows | `logos/windows.svg` | SVG | https://upload.wikimedia.org/wikipedia/commons/8/87/Windows_logo_-_2021.svg | Wikimedia Commons copy of official mark; trademark of owner | 2026-11-06 (est.) | — |
| x | `logos/x.svg` | SVG | https://commons.wikimedia.org/wiki/File:X_logo_2023.svg | Wikimedia Commons copy of official mark; trademark of owner | 2026-11-03 (est.) | jensen-returns |
| yahoo | `logos/yahoo.svg` | SVG | https://upload.wikimedia.org/wikipedia/commons/3/3a/Yahoo!_ | Trademark of owner (license not recorded) | 2026-11-04 | — |
| zookeeper | `logos/zookeeper.svg` | SVG | https://upload.wikimedia.org/wikipedia/commons/7/77/Apache_ZooKeeper_logo.svg | Wikimedia Commons copy of official mark; trademark of owner | 2026-10-31 | — |
| azure | `logos/azure.svg` | SVG | https://upload.wikimedia.org/wikipedia/commons/f/fa/Microsoft_Azure.svg | Wikimedia Commons copy of official mark; trademark of owner | 2026-11-19 | system-design-of-ai/07-provider-failover |
| irctc | `logos/irctc.svg` | SVG | https://upload.wikimedia.org/wikipedia/en/4/45/IRCTC_Logo.svg | Wikimedia copy of official mark; trademark of owner | 2026-11-19 | system-design-of-ai/07-provider-failover |
| rbi | `logos/rbi.svg` | SVG | https://commons.wikimedia.org/wiki/Special:Redirect/file/Seal_of_the_Reserve_Bank_of_India.svg | Wikimedia Commons copy of official seal; public-domain work, restricted insignia | 2026-11-19 | system-design-of-ai/07-provider-failover |
| openrouter | `logos/openrouter.svg` | SVG | https://cdn.jsdelivr.net/npm/simple-icons@latest/icons/openrouter.svg | Simple Icons (CC0 glyph); brand trademark of owner | 2026-11-19 | system-design-of-ai/07-provider-failover |
| portkey | `logos/portkey.svg` | SVG | https://cfassets.portkey.ai/logo/dew-color.svg (as used in github.com/Portkey-AI/gateway README) | Official asset; trademark of owner | 2026-11-19 | system-design-of-ai/07-provider-failover |
| litellm | `logos/litellm.svg` | SVG | https://docs.litellm.ai/img/brand/litellm-favicon.svg (LiteLLM docs brand folder; monogram) | Official asset; trademark of owner | 2026-11-19 | system-design-of-ai/07-provider-failover |
| meta | `logos/meta.svg` | SVG | https://upload.wikimedia.org/wikipedia/commons/7/7b/Meta_Platforms_Inc._logo.svg | Wikimedia Commons copy of official mark; trademark of owner (Llama is branded with the Meta logo + "Llama" text) | 2026-11-21 | system-design-of-ai/12-tokenizers |
| huggingface | `logos/huggingface.svg` | SVG | https://huggingface.co/datasets/huggingface/brand-assets/resolve/main/hf-logo.svg | Official Hugging Face brand asset; trademark of owner | 2026-11-21 | system-design-of-ai/12-tokenizers |
| sarvam | `logos/sarvam.svg` | SVG | https://assets.sarvam.ai/assets/brand/logos/sarvam-logo-black.svg | Official Sarvam AI asset; trademark of owner | 2026-11-21 | system-design-of-ai/12-tokenizers |
| nvidia | `logos/nvidia.svg` | SVG | https://cdn.jsdelivr.net/npm/simple-icons@13.21.0/icons/nvidia.svg | cc0 (simple-icons; trademark NVIDIA) | 2026-11-24 | jensen-returns |
| nasdaq | `logos/nasdaq.svg` | SVG | https://commons.wikimedia.org/wiki/File:NASDAQ_Logo.svg (Author: Nasdaq) | Wikimedia Commons, trademark (Nasdaq) | 2026-11-24 | jensen-returns |
| dennys | `logos/dennys.svg` | SVG | https://commons.wikimedia.org/wiki/File:Denny's_Logo_06.2022.svg | Wikimedia Commons copy of official 2022 mark; trademark of Denny's | 2026-11-24 | jensen-returns |
