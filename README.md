# people
Api de datos de personas del Paraguay.

## Ruc

### Ejemplo

`Curl`
```
curl -X 'GET' \
  'https://ruc-py.herokuapp.com/?ruc=5049813-4' \
  -H 'accept: application/json'
```

`Url de la petición`
```
https://ruc-py.herokuapp.com/?ruc=5049813-4
```

`Respuesta`

```json
{
  "ruc": "5049813-4",
  "razonsocial": "FERNANDEZ CACERES, BLAS ISAIAS"
}
```


## Roadmap
* <s>Base de datos de RUC auto actualizado.</s>
* Base de datos de personas basado en el padrón nacional.
