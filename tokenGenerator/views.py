from django.http import HttpResponse
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import Http404
from rest_framework.permissions import IsAuthenticated
import uuid
import time
import random
import threading

pool_list = list()
pool_dict = dict()


def delete_token(token):
    del pool_dict[token]
    pool_list.remove(token)


def unblock_token(token):
    try:
        temp_token = pool_dict[token]
        if temp_token[0] == 'A':
            pool_dict[token] = ['NA', time.time()]
            pool_list.append(token)

            return {token: pool_dict[token]}

    except KeyError as ex:
        return 'Invalid'


class GenerateUniqueToken(APIView):
    def get(self, request):
        try:
            unique_token = uuid.uuid1().hex

            pool_list.append(unique_token)

            pool_dict[unique_token] = ['NA', time.time()]

            return Response(pool_dict)

        except Exception as ex:
            return Response(str(ex))


class AssignUniqueToken(APIView):
    def get(self, request):
        try:
            selected_token = random.choice(pool_list)

            pool_list.remove(selected_token)
            pool_dict[selected_token] = ['A', time.time()]

            return Response(pool_dict)

        except Exception as ex:
            return Response(status=status.HTTP_404_NOT_FOUND)


class UnblockToken(APIView):
    def get(self, request):
        try:
            if 'token' in request.data:
                selected_token = request.data['token']

                unblocked_token = unblock_token(selected_token)

                if unblocked_token == 'Invalid':
                    return Response('Invalid Token!', status=status.HTTP_404_NOT_FOUND)

                return Response(unblocked_token)

        except Exception as ex:
            return Response(str(ex))


class DeleteToken(APIView):
    def get(self, request):
        try:
            if 'token' in request.data:
                selected_token = request.data['token']

                try:
                    if pool_dict[selected_token][0] == 'NA':
                        del pool_dict[selected_token]
                        pool_list.remove(selected_token)
                    else:
                        del pool_dict[selected_token]
                except KeyError as ex:
                    return Response('Invalid Token!', status=status.HTTP_404_NOT_FOUND)

            return Response('Token Deleted!')

        except Exception as ex:
            return Response(str(ex))


class KeepTokenAlive(APIView):
    def get(self, request):
        try:
            if len(pool_list) == 0:
                return Response(status=status.HTTP_404_NOT_FOUND)

            if 'token' in request.data:
                selected_token = request.data['token']

                try:
                    temp_token = pool_dict[selected_token]
                    pool_dict[selected_token][1] = time.time()
                except KeyError as ex:
                    return Response('Invalid Token!', status=status.HTTP_404_NOT_FOUND)

                return Response('Kept Token Alive')

        except Exception as ex:
            return Response(str(ex))


def check_token_status():
    while True:
        try:
            if len(pool_list) != 0:
                for pool_list_elem in pool_list:
                    if time.time() - pool_dict[pool_list_elem][1] > 20:
                        unblock_token(pool_list_elem)
                    if time.time() - pool_dict[pool_list_elem][1] > 60:
                        delete_token(pool_list_elem)
        except Exception as ex:
            pass


threading.Thread(target=check_token_status).start()


def home(request):
    try:
        return HttpResponse('<h1>Welcome to Token Problem</h1>')
    except Exception as ex:
        return HttpResponse('')
