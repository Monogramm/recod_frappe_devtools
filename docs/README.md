# **Recod Frappe DevTools** User Guide

This is the User Guide for **Recod Frappe DevTools**.

For the user guide and technical documentation, check the Frappe [app documentation](https://github.com/Monogramm/recod_frappe_devtools/blob/master/recod_frappe_devtools/docs) or compile it locally using [recod_frappe_devtools](https://github.com/Monogramm/recod_frappe_devtools).

## Contributing

For information about contributing, see the [Contributing page](https://github.com/Monogramm/recod_frappe_devtools/blob/master/CONTRIBUTING.md).

## Roadmap

See [Taiga.io](https://tree.taiga.io/project/monogrammbot-monogrammrecod_frappe_devtools/ "Taiga.io monogrammbot-monogrammrecod_frappe_devtools")

## Install

```sh
bench get-app https://github.com/Monogramm/recod_frappe_devtools
bench install-app recod_frappe_devtools
```

## Commands

Available commands:

-  `build-app-docs`
-  `build-app-uml`

### Build application documentation

```sh
bench build-app-docs app 
```

| Option        |    Description        | Examples  |
| ------------- | ------------- | -----:|
| --extension | Extension for uml files | svg, png |
| --target | Name of application | recod_frappe_devtools |
| --watch | Watch for changes and rewrite (in progress yet) |

Then, go to URL `/docs`.
You will see the generated documentation from your application.

#### Screenshots

<details>
<!--  TODO Add screen shots of sample documentation -->
</details>

### Build application UML Doctype diagram

```sh
bench build-app-uml /tmp/uml.png
```

| Option        |    Description        | Examples  |
| ------------- | ------------- | -----:|
| --modules | Modules of the application for which UML should be generated | agriculture, crm, education |
| --doctype | Generate UML for specific doctype | Item |

## License

Copyright © 2020 [Monogramm](https://github.com/Monogramm).<br />
This project is [AGPL v3](https://opensource.org/licenses/AGPL-3.0) licensed.
