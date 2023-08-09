import gitlab
import json
from pathlib import Path
from os import listdir
from Auxiliary import number_input, random_password, read_from_xsl


class GitLab:
    def __init__(self, url: str, token: str) -> None:
        self.gl = gitlab.Gitlab(url=url, private_token=token, ssl_verify=False)

    def get_projects(self):
        print('finding')
        projects = self.gl.projects.list(iterator=True, search='misc', all=True)
        print('listing:')
        for project in projects:
            print(project.name)

    def delete_project(self):
        self.gl.projects.get(5051)

    def get_groups(self):
        groups = self.gl.groups.list()
        for group in groups:
            print(group)

    def create_users_selection(self):
        print('Выберите способ добавления:')
        print('1. Вручную')
        print('2. Из матрицы ролей')
        print('0. Вернуться')
        selection: int = number_input()
        match selection:
            case 1:
                self.create_single_user(self.select_group())
            case 2:
                self.create_multiple_users(self.select_group())
            case 0:
                pass
            case _:
                print('Повторите ввод')

    def select_group(self):
        print('Добавить к группе?')
        print('1. Да')
        print('2. Нет')
        selection: int = number_input()
        group_id: int = 0
        match selection:
            case 1:
                print('Выберите группу:')
                groups = self.gl.groups.list()
                for group in groups:
                    print(f'{group.id} {group.name}')
                group_id: int = number_input()
            case 2:
                pass
            case _:
                print('Повторите ввод')
        return group_id

    def create_single_user(self, group_id: int):
        """Добавляет одного юзера в систему согласно вводу и сохраняет информацию о нем в лог"""
        print('Введите ФИО пользователя')
        name: str = input()
        print('Введите username')
        username: str = input()
        print('Введите email')
        email: str = input()
        user = self.gl.users.list(search=f'{email}')
        role: int = 0
        if len(user) == 0:
            try:
                if group_id != 0:
                    print('Выберите роль:')
                    print('1. Guest')
                    print('2. Reporter')
                    print('3. Developer')
                    print('4. Maintainer')
                    role: int = number_input()
                self.save_to_log(self.add_user(name, username, email, group_id, role * 10))
            except gitlab.exceptions.GitlabCreateError:
                print('Некорректные данные')
        else:
            print('Такой пользователь уже существует.'
                  f'ID = {user[0].id}'
                  f'Имя = {user[0].name}')

    def create_multiple_users(self, group_id: int):
        """Создает нескольких юзеров из матрицы ролей (таблицы xsl) и сохраняет информацию о них в лог"""
        users = read_from_xsl()
        role = 0
        created_users = []
        for user in users:
            if len(self.gl.users.list(search=f'{user.get("email")}')) == 0:
                try:
                    if group_id != 0:
                        role: int = self.select_role(user.get('role'))
                    created_users.append(
                        self.add_user(user['name'], user['email'].split('@')[0], user['email'], group_id, role))
                except (gitlab.exceptions.GitlabCreateError) as e:
                    print(e)
                    print('Некорректные данные')
            else:
                print(f'{user.get("email")} уже существует')
        self.save_to_log(created_users)

    def select_role(self, role: str):
        """Выбирает роль из матрицы ролей"""
        result: int = 30
        if role == 'Руководитель Проекта' or \
                role == 'Владелец Продукта' or \
                role == 'Архитектор' or role == 'Тим-лид Разработки':
            result = 40
        return result

    def add_user(self, name: str, username: str, email: str, group_id: int = 0, role: int = 0):
        """Добавляет юзера в систему, сохраняет инфу о добавленном юзере в словарь и возвращает его"""
        password: str = random_password()
        user = self.gl.users.create({
            'name': name,
            'username': username,
            'email': email,
            'password': password,
            'projects_limit': 0,
            'can_create_group': False,
            'external': True,
            'is_admin': False,
            'provider': 'openid_connect',
            'extern_uid': username,
            'skip_confirmation': True
            })
        if role != 0:
            self.add_user_to_group(user.id, group_id, role)
        user = {'Date': user.created_at, 'Username': user.username, 'Email': user.email, \
                'Initial_password': password, 'Projects_limit': user.projects_limit, \
                'Can_create_group': user.can_create_group, 'External': user.external, \
                'Is_admin': user.is_admin, 'identities': user.identities, 'Role': role, 'Group': group_id}
        return user

    def add_user_to_group(self, user_id: int, group_id: int, role: int):
        """Добавляет юзера в группу rosim"""
        group = self.gl.groups.get(group_id)
        match role:
            case 10:
                group.members.create({'user_id': user_id, 'access_level': gitlab.GUEST_ACCESS})
            case 20:
                group.members.create({'user_id': user_id, 'access_level': gitlab.REPORTER_ACCESS})
            case 30:
                group.members.create({'user_id': user_id, 'access_level': gitlab.DEVELOPER_ACCESS})
            case 40:
                group.members.create({'user_id': user_id, 'access_level': gitlab.MAINTAINER_ACCESS})
            case _:
                raise ValueError('Некорректная роль')

    def delete_users_selection(self):
        """Вызывает меню выбора удаления юзера"""
        print('Выберите способ удаления:')
        print('1. ID')
        print('2. Email')
        print('3. По логам')
        print('0. Вернуться')
        selection: int = number_input()
        match selection:
            case 1:
                print('Введите id пользователя')
                self.delete_single_user(id=number_input())
            case 2:
                print('Введите email пользователя')
                self.delete_single_user(email=input())
            case 3:
                self.delete_by_log()
            case 0:
                pass
            case _:
                print('Повторите ввод')

    def delete_single_user(self, id: int = 0, email: str = ""):
        """Удаляет одного юзера либо по id, либо по email"""
        if len(email) > 0:
            user = self.gl.users.list(search=f'{email}')
            if len(user) == 1:
                self.delete_confirm(self.gl.users.get(user[0].id))
            elif len(user) == 0:
                print('Пользователь не найден')
            else:
                print('Найдено несколько пользователей')
        elif id > 0:
            try:
                user = self.gl.users.get(id)
                self.delete_confirm(user)
            except gitlab.exceptions.GitlabGetError:
                print('Пользователь не найден')

    def delete_confirm(self, user):
        """Вызывает меню подтверждения удаления, чтобы возможно было перепроверить данные"""
        print('Удалить пользователя?')
        print(user.name, user.username)
        print('1. Да')
        print('2. Нет')
        selection: int = number_input()
        match selection:
            case 1:
                user.delete()
                print('Пользователь успешно удален')
            case _:
                pass

    def delete_by_log(self):
        Path('logs').mkdir(parents=True, exist_ok=True)
        logs = listdir('logs')
        print('Выберите нужный лог')
        print('0. Выйти')
        for number, log in enumerate(logs):
            print(number + 1, log)
        selection: int = number_input()
        if selection > 0:
            with open(f'logs/{logs[selection - 1]}', 'r') as file:
                users = json.load(file)
                print(users)

    def save_to_log(self, users):
        """Принимает на вход словарь или лист словарей с информацией о юзере, и сохраняет в файл в формате json"""
        Path('logs').mkdir(parents=True, exist_ok=True)
        logs = listdir('logs')
        with open(f'logs/log{len(logs)}.log', 'w') as file:
            json.dump(users, file, indent=4)
        with open(f'logs/log{len(logs)}.log', 'r') as file:
            print(json.load(file))

    def block_user(self):
        """Добавляет одного юзера в систему согласно вводу и сохраняет информацию о нем в лог"""
        print('Введите email')
        email: str = input()
        user = self.gl.users.list(search=f'{email}')
        print(user)
        if len(user) == 1:
            try:
                self.block_confirm(self.gl.users.get(user[0].id))
            except gitlab.exceptions.GitlabCreateError:
                print('Некорректные данные')
        elif len(user) == 0:
            print('Такого пользователя не существует.')
        else:
            print('Найдено больше одного пользоавтеля')

    def block_confirm(self, user):
        """Вызывает меню подтверждения удаления, чтобы возможно было перепроверить данные"""
        print('Удалить пользователя?')
        print(user.id, user.name, user.username)
        print('1. Да')
        print('2. Нет')
        selection: int = number_input()
        match selection:
            case 1:
                user.block()
                print('Пользователь успешно заблокирован')
            case _:
                pass
