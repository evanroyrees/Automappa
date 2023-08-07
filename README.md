# Automappa: An interactive interface for exploration of metagenomes

![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/WiscEvan/Automappa?label=latest) <a href="https://github.com/WiscEvan/Automappa/contribute"><img src="https://img.shields.io/badge/Contribute-blue" alt="Contributing"/></a>

| Image Name           | Image Tag       | Status | Size |
|----------------------|-----------------|--------|-----|
| `evanrees/automappa` | `main`,`latest` | [![docker CI/CD](https://github.com/WiscEvan/Automappa/actions/workflows/docker.yml/badge.svg?branch=main "evanrees/automappa:main")](https://github.com/WiscEvan/Automappa/actions/workflows/docker.yml) | ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/evanrees/automappa/main) |
| `evanrees/automappa` | `develop`       | [![develop docker CI/CD](https://github.com/WiscEvan/Automappa/actions/workflows/docker.yml/badge.svg?branch=develop "evanrees/automappa:develop")](https://github.com/WiscEvan/Automappa/actions/workflows/docker.yml) | ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/evanrees/automappa/develop) |

https://github.com/WiscEvan/Automappa/assets/25933122/4de76297-f5a2-42d4-bf5e-8d695c3ef4fe

> You may also [see each page as a static view](docs/page-overview.md)

## :deciduous_tree: Automappa testing setup/run commands

- [Clone the Automappa Repo](#clone-the-automappa-repository)
- [Run `make build` using Makefile](#build-images-for-services-used-by-automappa)
- [Run `make up` using Makefile](#build-and-run-automappa-services)
- [Open the Automappa url](#navigate-to-automappa-page)
- [Download test data](#download-test-data)

## Miscellaneous

- [Using Automappa on a remote server](docs/remote-server.md)

### clone the Automappa Repository

```bash
git clone https://github.com/WiscEvan/Automappa
```

### build images for services used by Automappa

```bash
make build
```

### build and run automappa services

> You can skip `make build` if you’d like, as this command will build and pull any images not available.

```bash
make up
```

> NOTE: If your computer is already using most of its resources, you may need to close
some applications so docker may construct all of the necessary Automappa services

### Navigate to Automappa page

Once you see `automappa_web_1` running from the terminal logs, you should be able to navigate to <localhost:8050> 🥳

### Download Test Data

Test data to try out Automappa may be downloaded from the google drive in the [Automappa test data folder](<https://drive.google.com/drive/folders/1nBk0AZC3EJV4t-9KdJBShGCfWbdP2kOp?usp=sharing>)

Try out different settings and perform your own refinements on some of this sponge data!

>NOTE: This dataset was retrieved from:
>
> Uppal, Siddharth, Jackie L. Metz, René K. M. Xavier, Keshav Kumar Nepal, Dongbo Xu, Guojun Wang, and Jason C. Kwan. 2022. “Uncovering Lasonolide A Biosynthesis Using Genome-Resolved Metagenomics.” mBio 13 (5): e0152422.

Happy binning!


## Contributors

![Automappa's Contributors](https://contrib.rocks/image?repo=WiscEvan/Automappa)
