# GWAS Catalog: Beyond SNPs

[![CI](https://github.com/EBISPOT/gwas-beyond-snps/actions/workflows/ci.yaml/badge.svg?branch=main)](https://github.com/EBISPOT/gwas-beyond-snps/actions/workflows/ci.yaml)
![PyPI - Version](https://img.shields.io/pypi/v/gwascatalog.sumstatapp)

This Python monorepo contains packages and documentation designed to help users prepare non-SNP GWAS summary statistics for submission to the [GWAS Catalog](https://ebi.ac.uk/gwas).

## What kind of data are supported?

| Type of genetic variant              | Supported                                                                     |
|--------------------------------------|-------------------------------------------------------------------------------|
| Single nucleotide polymorphism (SNP) | ❌, see [`gwas-sumstats-tools`](https://github.com/ebispot/gwas-sumstats-tools) |
| Copy number variant (CNV)            | ✅                                                                            |
| Gene                                 | ✅                                                                            |

## Using the validation CLI for bulk data processing


> [!TIP]
> If you prefer not to work in a terminal or you [find it difficult to use please try the web app](https://www.ebi.ac.uk/gwas/apps/beyond-snps/validate/)


First, [install uv](https://docs.astral.sh/uv/), then run:

```
$ uvx --from gwascatalog-sumstatapp gwascatalog beyondsnp validate --help
```

You should see:

```
Validate GWAS summary statistics files for submission to the GWAS Catalog.

positional arguments:
  INPUT                 Files to validate

options:
  -h, --help            show this help message and exit
  --type {CNV,GENE}     Type of genetic variation (CNV or GENE)
  --assembly {GRCh38,GRCh37,NCBI36,NCBI35,NCBI34}
                        Genome assembly (e.g. GRCh38)
  --effect-size {beta,odds_ratio,hazard_ratio,z_score}
                        Primary effect size measure
  --allow-zero-pvalues  Accept zero as a valid p-value
  -o, --output-dir OUTPUT_DIR
                        Output directory for results (default: ./validated/)
```

The package is [also available from PyPI](https://pypi.org/project/gwascatalog.sumstatapp/). You should always install the `pydantic` extra:

```
$ pipx install "gwascatalog.sumstatapp[pydantic]"
```

## Documentation

See [our docs here](https://www.ebi.ac.uk/gwas/apps/beyond-snps/). Please create an issue or email gwas-info@ebi.ac.uk if you have any questions or comments. We appreciate community feedback.

## Developer notes 

This repository is a [`uv`](https://docs.astral.sh/uv/) workspace containing two Python packages:

- `sumstatlib`: [Pydantic models and validation public interfaces](sumstatlib)
- `sumstatapp`: data validation applications which uses sumstatlib internally, containing two deployment approaches:
  - A [Pyodide](https://github.com/pyodide/pyodide) web application, [responsible for browser-based data validation](src/gwascatalog/sumstatapp/web)
  - A [standard CLI for bulk data processing](src/gwascatalog/sumstatapp/cli) and eventual integration with the GWAS Catalog backend

### User facing website

* The `docs` directory contains a [docusaurus](https://docusaurus.io/) website
* This is the landing page for non-SNP GWAS Catalog submissions at https://www.ebi.ac.uk/gwas/apps/beyond-snps/
* A [custom docusaurus build process](docs/package.json#L11) is responsible for building the sumstatlib wheel and bundling the sumstatapp web directory as static content

### Building the beyond SNPs static site

Local preview build (served at `/`; this is not the EBI development deployment):

```
$ cd docs
$ npm run build:dev
$ npm run serve 
```

Production build (served at `/gwas/apps/beyond-snps/`):

```
$ cd docs
$ npm run build
```

EBI development uses the same path, with a different hostname:

```sh
cd docs
DOCUSAURUS_URL=https://wwwdev.ebi.ac.uk npm run build
```

### GitLab Pages and VTM

GitLab Pages stores the static site; VTM exposes it at the public EBI URL.
The public path is always `/gwas/apps/beyond-snps/`, including assets and the
validator. Production uses `www.ebi.ac.uk`; development uses `wwwdev.ebi.ac.uk`.
The Pages `/dev/` prefix is internal and must not appear in browser-facing paths.

The GitLab pipeline runs lint, tests and the site build for branches and merge
requests. Successful default-branch pipelines publish production automatically.
Successful protected `dev` branch pipelines publish the separate development
deployment. Both deployments have no automatic expiry. GitHub CI also builds
the site for proposed changes.

Before switching traffic, configure VTM using the existing GWAS documentation
Pages rules as the model:

- Set the upstream Host header to `gwas.gitdocs.ebi.ac.uk` and use the
  `gwas-gitdocs` pool.
- Replace the public `/gwas/apps/beyond-snps/` prefix with the project's Pages
  path for production, and that path followed by `dev/` for development.
  Confirm the project path in GitLab's **Deploy > Pages** settings.
- Redirect the bare application path and extensionless directory routes to
  their trailing-slash public URLs before proxying. Preserve query strings.
  This prevents upstream redirects from exposing the internal Pages hostname.
- Replace the existing production `gwas-beyond-snps` Kubernetes route and add
  the development route before the general GWAS fallback.

Publishing Pages alone does not change VTM or retire existing Kubernetes
workloads. Confirm anonymous access, GitHub-to-GitLab mirroring, a `gwas` runner,
the group Dependency Proxy, protected `dev`, and environment deployment
permissions. Pages requires GitLab 17.10+ for this configuration; development
also requires a parallel deployment slot on Premium or Ultimate.

After the VTM switch, check both public hostnames: documentation navigation,
direct links with and without trailing slashes, validator startup, wheel
loading, validation and downloading a result. Missing scripts must return 404.
Use the public environment links rather than the internal Pages URLs.

For rollback, retry publication from a known-good pipeline. Rebuild that commit
on the appropriate deployment branch if its build artefact has expired. Keep
the previous VTM route available until the Pages deployment has been accepted.

