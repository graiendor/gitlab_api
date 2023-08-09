from DB.base import Session, Base, engine
from DB.Instrument import Instrument
from GitLabApi import GitLab
from Auxiliary import number_input
from pathlib import Path


class Service:
    def __init__(self) -> None:
        Base.metadata.create_all(engine)
        self.session = Session()
        self.stop = False
        self.consistent = False
        self.instrument = None
        self.gitlab = None

    def run(self) -> None:
        """Запускает сервис, пока тот не будет остановлен установкой флага stop"""
        while not self.stop:
            self.consistent: bool = self.check_consistency()
            self.menu()
            selection: int = number_input()
            match selection:
                case 1:
                    self.instrument_addition()
                case 2:
                    if self.consistent: self.instrument_selection()
                case 0:
                    self.stop = True
                case _:
                    print('Неверный выбор.')

    def menu(self) -> None:
        """Выводит начальное меню, которое появляется при запуске сервиса"""
        print('Меню')
        print('1. Добавить инструмент')
        if self.consistent: print('2. Выбрать инструмент')

    def instrument_addition(self) -> bool:
        """Добавляет инструмент (его аттрибуты) в базу данных.
        Возвращает True, если инструмент добавлен успешно"""
        added: bool = False
        print('Введите название инструмента: ')
        name: str = input()
        print('Введите адрес инструмента (например: https://*/gitlab/): ')
        adddress: str = input()
        print('Введите свой токен: ')
        token: str = input()
        try:
            self.session.add(Instrument(name=name, address=adddress, token=token))
            print('Инструмент успешно добавлен.')
            self.session.commit()
            self.session.close()
            added = True
        except:
            print('Что-то пошло не так.')
        return added

    def instrument_selection(self) -> None:
        """Выбирает аттрибуты инструмента из базы данных и помещает в self.instrument.
        Далее вызывает token_check"""
        instruments = self.session.query(Instrument).all()
        for number, instrument in enumerate(instruments):
            print(f'{number + 1}: {instrument.name}')
        print('Выберите нужный инструмент')
        selection: int = number_input()
        if selection in range(1, len(instruments) + 1):
            instrument = instruments[selection - 1]
            self.instrument = instrument
            self.token_check()
        else:
            print('Некорретный выбор')

    def token_check(self) -> None:
        """Проверяет наличие токена в инструменте. 
        Если его нет, предлагает ввести, и добавляет в базу данных
        Далее вызывает function_selection"""
        if not self.instrument.token:
            print('Введите ваш личный токен: ')
            self.update_field('token')
        self.function_selection()

    def function_selection(self):
        """Выводит меню выбора действий, которые можно совершить с помощью инструмента"""
        self.gitlab = GitLab(url=self.instrument.address, token=self.instrument.token)
        print(f'Инструмент - {self.instrument.name}')
        print('1. Добавить пользователей')
        print('2. Удалить пользователей')
        print('3. Заблокировать пользователей')
        print('4. Удалить все логи')
        print('5. Изменить название')
        print('6. Изменить адрес')
        print('7. Изменить токен')
        print('0. Выйти')
        selection: int = number_input()
        match selection:
            case 1:
                self.gitlab.create_users_selection()
            case 2:
                self.gitlab.delete_users_selection()
            case 3:
                self.gitlab.block_user()
            case 4:
                Path('logs').rmdir()
            case 5:
                print('Введите новое название: ')
                self.update_field('name')
            case 6:
                print('Введите новый адрес: ')
                self.update_field('address')
            case 7:
                print('Введите новый токен: ')
                self.update_field('token')
            case 9:
                self.gitlab.get_groups()
            case 0:
                pass
            case _:
                print('Повторите выбор')

    def update_field(self, field: str):
        """Обновляет поле в бд согласно вводу"""
        self.session.query(Instrument) \
            .filter(Instrument.id == self.instrument.id) \
            .update({field: input()})
        self.session.commit()
        self.session.close()

    def check_consistency(self) -> bool:
        "Проверяет, есть ли в базе данных данные и возвращает False, если нет"
        return True if self.session.query(Instrument).first() else False
