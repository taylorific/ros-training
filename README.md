# ROS Training

To start the slide show:

```
docker run -it --rm \
  --mount type=bind,source="$(pwd)",target="/slidev" \
  --publish 3030:3030 \
  docker.io/boxcutter/slidev

# Visit <http:/localhost:3030/>
```

Edit the [slides.md](./slides.md) to see the changes.

# Table of contents check

Only section slides (`layout: section`) appear in the table of contents; every
other slide needs `hideInToc: true`, and each section slide links back to the
TOC with `<Link to="toc" .../>`. Check this before pushing (CI runs it too):

```bash
python3 scripts/check_toc.py
```

Learn more about Slidev at the [documentation](https://sli.dev/).

# Update dependencies

To see what is out of date:

```bash
docker run -it --rm \
  --mount type=bind,source="$(pwd)",target="/slidev" \
  --entrypoint npm \
  docker.io/boxcutter/slidev outdated
```

To upgrade Slidev and the themes to their latest versions:

```bash
docker run -it --rm \
  --mount type=bind,source="$(pwd)",target="/slidev" \
  --entrypoint npm \
  docker.io/boxcutter/slidev \
    install @slidev/cli@latest @slidev/theme-default@latest @slidev/theme-seriph@latest

# on the host
git add package.json package-lock.json
git commit -m "Sync npm lockfile"
git push
```

# Attributions

The following projects were used for inspiration and some code was
reused for the slideware:

- https://sli.dev/ - Slidev slideware
- https://github.com/alexanderdavide/slidev-theme-academic  Pagination  - Alexander Eble
- https://github.com/jpetazzo/container.training - Idea of using markdown slideware for training - Jérôme Petazzoni
