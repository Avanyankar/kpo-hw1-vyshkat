# ВышКат — учёт парка кикшеринга

Домашнее задание №1 по курсу «Конструирование программного обеспечения»: консольное
приложение учёта парка сервиса «ВышКат». Условие — в файле `КПО-ДЗ-1-кикшеринг-ВШЭ.pdf`.

## Стек

- **Python 3.12+**
- **[uv](https://docs.astral.sh/uv/)**
- **[ruff](https://docs.astral.sh/ruff/)**
- **[mypy](https://mypy.readthedocs.io/)**
- **[pytest](https://docs.pytest.org/)**, **[pytest-cov](https://pytest-cov.readthedocs.io/)**
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

## Использование

Приложение читает текстовые команды: с клавиатуры (`make run`) или из файла
(`uv run vyshkat <файл>`). Демонстрация всех сценариев — `make demo`, сценарий лежит в
[`scenarios/demo.txt`](scenarios/demo.txt).

| Команда | Что делает |
|---|---|
| `accept <вид> "<название>" simplicity=N condition=N [energy=X]` | принять технику; перед приёмкой — техосмотр |
| `add <вид> "<название>" [energy=X]` | поставить вещь на баланс, без осмотра |
| `report` | число единиц (всего, техника / вещи, по видам) и суточный расход энергии |
| `newbies` | техника, которую можно выдавать новичкам |
| `inventory` | номера, виды и наименования всего на балансе |
| `kinds` | виды и их параметры: техника `scooter`, `ebike`, `bicycle`; вещи `helmet`, `dock`, `cabinet` |
| `help`, `exit` | справка, выход |

Параметры пишутся как `ключ=значение` в любом порядке, дробные — через точку. Название с
пробелами — в кавычках; знак `=` в названии не поддерживается. Строки с `#` — комментарии.

```
> accept scooter "Ninebot Max G30" simplicity=7 condition=8 energy=0.45
Принят: INV-0001 Электросамокат «Ninebot Max G30»
> accept scooter "Xiaomi M365" simplicity=8 condition=3 energy=0.3
Отказ: Электросамокат «Xiaomi M365» — состояние 3/10 ниже порога 5
> add helmet "Шлем M"
Поставлен на баланс: INV-0002 Шлем «Шлем M»
> accept bicycle "Stels" simplicity=15 condition=5
Ошибка: simplicity=15 — простота: ожидается от 1 до 10, получено 15
> inventory
INV-0001  Электросамокат  Ninebot Max G30
INV-0002  Шлем            Шлем M
```

Ошибка ввода не останавливает работу: приложение сообщает о ней и ждёт следующую команду.

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

## Расширение: новый вид техники или вещи

Например, электроскутер:

1. **Домен** — класс-наследник в `domain/vehicles.py` (для вещи — в `domain/things.py`):

   ```python
   @dataclass(frozen=True)
   class EScooter(Vehicle):
       daily_energy_kwh: float
       kind: ClassVar[str] = "Электроскутер"

       def __post_init__(self) -> None:
           super().__post_init__()
           require_positive("суточный расход", self.daily_energy_kwh)
   ```

2. **Консоль** — строка в `VEHICLE_KINDS` (для вещи — в `THING_KINDS`) в `cli/catalog.py`:
   имя для команды, фабрика из параметров и подсказка по параметрам.
