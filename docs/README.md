# **Recod Frappe DevTools** User Guide

This is the User Guide for **Recod Frappe DevTools**.

## Recod Frappe DevTools

Frappe application to provide more/better development tools.

## Roadmap

See [Taiga.io](https://tree.taiga.io/project/monogrammbot-monogrammrecod_frappe_devtools/ "Taiga.io monogrammbot-monogrammrecod_frappe_devtools")

## How to use this application

```sh
bench build-app-docs
```

## Install

**Install Frappe application**

```sh
bench get-app https://github.com/Monogramm/recod_frappe_devtools
bench install-app recod_frappe_devtools
```

## Usage

How to use this application:

Run command
```sh
bench build-app-docs
```


and refer to url `/docs`. You will see the generated docs from `recod_frappe_devtools/docs` folder.

## List with options

```sh
bench build-app-docs
```
| Option        |    Description        | Examples  |
| ------------- |:-------------:| -----:|
| --extension      | extension for uml files | svg, png |
| --target            | Name of application      |   recod_frappe_devtools |
| --watch            | Watch for changes and rewrite (in progress yet)      |    |

----

```sh
bench build-app-uml
```

| Option        |    Description        | Examples  |
| ------------- |:-------------:| -----:|
| --modules      | List with modules | argiculture, crm, education |
| --doctype            | Generate uml for definetely doctype      |   Item |

## License

Copyright © 2020 [Monogramm](https://github.com/Monogramm).<br />
This project is [AGPL v3](https://opensource.org/licenses/AGPL-3.0) licensed.