# ВышКат — учёт парка кикшеринга

Домашнее задание №1 по курсу «Конструирование программного обеспечения»: консольное
приложение учёта парка сервиса «ВышКат». Условие — в файле `КПО-ДЗ-1-кикшеринг-ВШЭ.pdf`.

## Стек

- **Python 3.12+**
- **[uv](https://docs.astral.sh/uv/)**
- **[ruff](https://docs.astral.sh/ruff/)**
- **[mypy](https://mypy.readthedocs.io/)**
- **[pytest](https://docs.pytest.org/)**

## Установка и запуск

Добавлен Makefile для удобства, чтобы посмотреть команды:

```bash
make
```

Для запуска необходим [uv](https://docs.astral.sh/uv/getting-started/installation/).
Первый запуск:

```bash
make install
make run
```

## Доменная модель

Код: `src/vyshkat/domain/`.

| Тип | Что это | Потребляет энергию |
|---|---|---|
| `Vehicle`: `Scooter`, `EBike`, `Bicycle` | Прокатный транспорт: название, простота для новичка (1–10), техсостояние (1–10) | `Scooter`, `EBike` |
| `Thing`: `Helmet`, `DockStation`, `ChargingCabinet` | Вещи на балансе | `DockStation`, `ChargingCabinet` |
| `InventoryItem(number, asset)` | Актив, принятый на баланс | — |

Абстракции из задания — протоколы в `protocols.py`:

- `EnergyConsumer` — суточный расход энергии, кВт·ч;
- `Inventoried` — инвентарный номер и наименование; реализует `InventoryItem`.

**Почему номер не в самом самокате.** У предложенного к приёмке объекта номера нет вообще:
он появляется только при постановке на баланс, вместе с обёрткой `InventoryItem`. Если бы
номер был полем `Scooter`, то до приёмки он был бы пустым или выдавался бы до техосмотра и
сгорал при отказе.

## Приёмка

Код: `src/vyshkat/services/`.

```
accept_vehicle(vehicle) ──► ServiceCenter.inspect(vehicle)
                              ├─ отказ ──► Rejected(reason), номер не выдаётся
                              └─ годен ──► номер INV-NNNN ──► InventoryItem ──► Fleet ──► Accepted(item)

add_thing(thing) ─────────────────────────► номер INV-NNNN ──► InventoryItem ──► Fleet ──► Accepted(item)
```

- `ServiceCenter` — протокол техосмотра. Реализация `ConditionServiceCenter` принимает
  транспорт с техсостоянием не ниже порога (по умолчанию 5).
- `InventoryNumberGenerator` — одна серия номеров на технику и вещи.
- `Fleet` — записи на балансе; повторный номер отклоняется.
