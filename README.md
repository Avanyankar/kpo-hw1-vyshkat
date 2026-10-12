# ВышКат — учёт парка кикшеринга

Домашнее задание №1 по курсу «Конструирование программного обеспечения»: консольное
приложение учёта парка сервиса «ВышКат». Условие — в файле `КПО-ДЗ-1-кикшеринг-ВШЭ.pdf`.

## Стек

- **Python 3.12+**
- **[uv](https://docs.astral.sh/uv/)**
- **[ruff](https://docs.astral.sh/ruff/)**
- **[mypy](https://mypy.readthedocs.io/)**
- **[pytest](https://docs.pytest.org/)**
- **[punq](https://github.com/bobthemighty/punq)**: DI-контейнер

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
- `Inventoried` — строка инвентарной ведомости: номер, вид, наименование; его реализует
  `InventoryItem`. Состав протокола задаёт его потребитель — отчёт по номерам (ISP).

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

## Отчёты

`FleetReports` (`services/reports.py`) строит отчёты только по тому, что стоит на балансе:

| Отчёт | Как считается |
|---|---|
| Число единиц | всего, техника / вещи, разбивка по видам |
| Суточный расход энергии | сумма по активам, которые являются `EnergyConsumer` |
| Техника для новичков | транспорт, который одобряет `NewbiePolicy`: простота ≥ 6 |
| Номера, виды и наименования | всё на балансе; отчёт видит записи только как `Inventoried` |

## DI-контейнер

Composition root — `src/vyshkat/container.py`, функция `build_container()`. Только здесь решается,
какая реализация стоит за абстракцией; остальные классы получают зависимости через конструктор
и про контейнер не знают.

| Регистрация | Время жизни | Почему |
|---|---|---|
| `Fleet`, `InventoryNumberGenerator` | один экземпляр на приложение | это состояние учёта: приёмка и отчёты должны видеть один парк и одну серию номеров |
| `ServiceCenter` → `ConditionServiceCenter` | новый при каждом запросе | без состояния |
| `NewbiePolicy`, `AcceptanceService`, `FleetReports` | новый при каждом запросе | без собственного состояния, общее берут из одиночек выше |

Подмена техосмотра в тестах (`tests/test_container.py`): поверх готового контейнера
регистрируется фейк, и приёмка, полученная из контейнера, осматривает уже через него:

```python
container = build_container()
container.register(ServiceCenter, instance=FakeServiceCenter(Verdict(False, "...")))
container.resolve(AcceptanceService)  # внутри — фейк
```
