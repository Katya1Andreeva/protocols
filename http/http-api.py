import vk_api
import sys
import argparse


# Print iterations progress
def print_progress_bar(iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█', printEnd="\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    sys.stdout.write(f'\r{prefix} |{bar}| {percent}% {suffix}')
    sys.stdout.flush()
    # Print New Line on Complete
    if iteration == total:
        print()


class Friend:
    def __init__(self, first_name, last_name, popularity):
        self.first_name = first_name
        self.last_name = last_name
        self.popularity = popularity

    def __str__(self):
        return "{0} {1} популярность: {2}".format(self.first_name, self.last_name, self.popularity)

    def __lt__(self, other):
        return self.popularity < other.popularity


class VkRequest:
    def __init__(self, vk_session):
        self.api = vk_session.get_api()  # Позволяет обращаться к методам API как к обычным классам.(нр vk.wall.get(…))

    @staticmethod
    def calc_user_popularity(friends_count, likes_count):
        return friends_count * 2 + likes_count * 5

    def get_profile_photos_likes_count(self, id):
        count = 0
        photo_data = self.api.photos.get(album_id='profile', owner_id=id, extended=1)
        for photo_info in photo_data['items']:
            count += photo_info['likes']['count']

        return count

    def get_user_popularity(self, id):
        likes_count = self.get_profile_photos_likes_count(id)
        friends_count = \
            self.api.friends.get(fields="uid,first_name,last_name,photo,country,city,sex,bdate", user_id=id)['count']

        return self.calc_user_popularity(friends_count, likes_count)

    def get_friends_with_popularity(self, friends):
        for friend in friends:
            try:
                popularity = self.get_user_popularity(friend['id'])
                yield Friend(friend['first_name'], friend['last_name'], popularity)
            except Exception as e:
                yield Friend(friend['first_name'], friend['last_name'], -1)

    def get_friends_by_id(self, id, amount):
        if amount != -1:
            return self.api.friends.get(user_id=id, fields="uid,first_name,last_name,photo,country,city,sex,bdate",
                                        count=int(amount))
        return self.api.friends.get(user_id=id, fields="uid,first_name,last_name,photo,country,city,sex,bdate")


def main_autor():
    app = 4821803  # app_id Standalone-приложения
    secret = 'BfwdA9SgBp3LpJ0ToErw'  # Защищенный ключ приложения для Client Credentials Flow авторизации приложения

    vk_session = vk_api.VkApi(app_id=app, client_secret=secret)

    try:
        vk_session.server_auth()
        return vk_session
    except vk_api.AuthError as error_msg:
        print(error_msg)
        return


def main():
    parser = argparse.ArgumentParser()
    #аргумент а - количество друзей, если его не передовать, то берем всех друзей
    parser.add_argument('-a', '--amount', default=-1, type=int)
    parser.add_argument('-i', '--id', type=int)
    args = parser.parse_args()
    amount = args.amount
    id = args.id
    if id is None:
        print("No id!")
        sys.exit()
    vk_session = main_autor()
    request = VkRequest(vk_session)

    if request.api.users.get(user_id=id, fields="is_closed")[-1]['is_closed']:
        print("Profile is private!")
        sys.exit()
    friends = request.get_friends_by_id(id, amount)

    friends_generator = request.get_friends_with_popularity(friends['items'])
    if amount != -1:
        print_progress_bar(0, amount, prefix='Progress:', suffix='Complete', length=50)
    else:
        print_progress_bar(0, friends['count'], prefix='Progress:', suffix='Complete', length=50)
    result = []

    for friend in friends_generator:
        result.append(friend)
        if amount != -1:
            print_progress_bar(len(result), amount, prefix='Progress:', suffix='Complete', length=50)
        else:
            print_progress_bar(len(result), friends['count'], prefix='Progress:', suffix='Complete', length=50)
    sorted_friends = sorted(result, key=lambda f: f.popularity, reverse=True)
    for f in sorted_friends:
        print(f)


if __name__ == '__main__':
    main()

    #  проверяем закрытый профиль или нет и добавить ограничение по количеству друзей как ключ к запуску
