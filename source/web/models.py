from uuid import uuid4
from django.contrib.auth.models import User
from django.db import models
from web.helpers import Generator
from django.db.models import Q
from django.conf import settings
from django.utils import timezone


class Purge(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    field = models.CharField(max_length=128, blank=True, default='')
    grade = models.CharField(max_length=128, blank=True, default='')
    level = models.IntegerField(default=0)
    xp = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)


# TODO contest_id must be add when the first user fill a room
# this manager is for handling the waiting contests

class PurgeManager(models.Manager):
    # this manger returns a contest as a room for the players
    def search_opponent(self, username):
        # second_user = user.username
        # the_user = Profile.objects.filter(user__username=username).get()
        the_user = Contestant.objects.filter(profile__user__username=username).get()

        # matchmaking filters
        qlookup_is_second_empty = Q(second_user=None)
        qlookup_field = Q(first_user__profile__field=the_user.profile.field)
        qlookup_grade = Q(first_user__profile__grade=the_user.profile.grade)
        qlookup_level = Q(first_user__profile__level__range=(the_user.profile.level-5,the_user.profile.level+5))
        qlookup_except_me = ~Q(first_user__profile__user__username=the_user.profile.user.username)

        #Limit Players
        qlookup_contestant_limit = Q(first_user__profile__user__username=the_user.profile.user.username)|Q(second_user__profile__user__username=the_user.profile.user.username)

        players_live_contests_num = 0
        for contest in self.get_queryset().filter(qlookup_contestant_limit):
            players_live_contests_num += 1

        if players_live_contests_num >=5:
                print("you reached the 5 games limit")
                return
        else:
            pass

        #Check Available Matches
        available_matches = self.get_queryset().filter(qlookup_is_second_empty & qlookup_field & qlookup_grade & qlookup_except_me & qlookup_level)

        # no opponent found in same level range, level will be ignored
        if not available_matches.exists():
            available_matches = self.get_queryset().filter(
                qlookup_is_second_empty & qlookup_field & qlookup_grade & qlookup_except_me).distinct()

        # match found. the user will be the second user in contest
        if available_matches.exists():
            # not repetitive match!search more and more...
            for contest in available_matches:
                print(contest.first_user)
                if Contest.objects.filter(
                        Q(first_user=contest.first_user, second_user=the_user) | Q(first_user=the_user,
                                                                                   second_user=
                                                                                   contest.first_user)).exists():
                    if contest==available_matches.last():######check last or finished
                        print("All contest were repetitive,no opponent found, this opponent will be rooms first_user")
                        the_uuid = str(uuid4().hex[:16])
                        f_user = str(the_user)
                        CID = f_user + the_uuid
                        new_contest_room = Contest.objects.get_or_create(first_user=the_user, second_user=None, CID=CID)
                        print(new_contest_room)
                        print(new_contest_room[0])
                        return new_contest_room[0]
                    else:
                        pass
                elif not Contest.objects.filter(
                        Q(first_user=contest.first_user, second_user=the_user) | Q(first_user=the_user,
                                                                                                second_user=
                                                                                               contest.first_user)).exists():
                    found_contest = Contest.objects.filter(first_user=contest.first_user, second_user=None).first()
                    found_contest.second_user = the_user
                    found_contest.save()
                    print("Opponent found, this opponent will be rooms second_user")
                    print(found_contest)
                    return found_contest
                # else:#does it ever run??????????????????????????????
                #     print("No Opponent found, this opponent will be rooms first_user")
                #     new_contest_room = Contest.objects.get_or_create(first_user=the_user, second_user=None)
                #     print(new_contest_room)
                #     print(new_contest_room[0])
                #     return new_contest_room[0]
        else:
            print("No contest exists,No opponent found, this opponent will be rooms first_user")
            the_uuid = str(uuid4().hex[:16])
            f_user = str(the_user)
            CID = f_user + the_uuid
            new_contest_room = Contest.objects.get_or_create(first_user=the_user, second_user=None, CID=CID)


            print(new_contest_room)
            print(new_contest_room[0])
            return new_contest_room[0]



class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)
    cityId = models.PositiveIntegerField(null=True)
    field = models.CharField(max_length=128, blank=True, default='')
    grade = models.CharField(max_length=128, blank=True, default='')
    phoneNumber = models.CharField(max_length=128, blank=True, default='')
    experience = models.FloatField(default=0)
    level = models.IntegerField(default=0)
    consumable = models.PositiveIntegerField(default=0)
    guest = models.BooleanField(default=True)

    # TODO is_ban(bool) and ban_date (dateField)

    class Meta:
        ordering = ('created',)

    def __str__(self):
        return "{0}:{1}".format(self.created, self.user.username)


class Token(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=128)

    def save(self, *args, **kwargs):
        self.token = Generator.generate_uuid(Token, 'token')
        super(Token, self).save(*args, **kwargs)

    def __str__(self):
        return "{}: token_{}".format(self.user, self.token)


class Contestant(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    state = models.CharField(max_length=128, blank=True, default='')
    contest_id = models.CharField(max_length=128, blank=True, default='')
    join_flag = models.BooleanField()

    def __str__(self):
        return "{0}".format(self.profile.user.username)


class Contest(models.Model):
    # TODO do the related__name stuff
    first_user = models.ForeignKey(Contestant, on_delete=models.CASCADE, related_name='first_user')
    second_user = models.ForeignKey(Contestant, on_delete=models.CASCADE, related_name='second_user', default=None, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    CID = models.CharField(max_length=167, default=None, blank=True)
    #
    # def save(self, *args, **kwargs):
    #     the_uuid = str(uuid4().hex[:16])
    #     first_user = str(User.objects.filter(username=self.first_user).get().username)
    #     self.CID = first_user + the_uuid

    # field = models.CharField(max_length=128, blank=True, default='')
    # grade = models.CharField(max_length=128, blank=True, default='')
    # level = models.IntegerField(default=0)
    # # xp = models.IntegerField(default=0)
    #
    # def save(self, *args, **kwargs):
    #     self.field = self.first_user.profile.field
    #     self.grade = self.first_user.profile.grade
    #     self.level = self.first_user.profile.level
    #
    #     super(Contest, self).save(*args, **kwargs)

    objects = PurgeManager()

    def __str__(self):
        return "{0} vs {1}".format(self.first_user, self.second_user)


########################################################################################################################
# Shop #################################################################################################################
########################################################################################################################
class Shop(models.Model):
    version = models.IntegerField()
    image = models.ImageField(upload_to='static/images/shop/', default='static/images/shop/money.jpg')
    title = models.CharField(max_length=128, blank=True, default='')

    def __str__(self):
        return "shop_version: {}".format(self.version)


class ShopItem(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, default=None)
    item_id = models.IntegerField(primary_key=True,blank=True,editable=False)
    title = models.CharField(max_length=128, blank=True, default='')
    info = models.CharField(max_length=128, blank=True, default='')
    image = models.ImageField(upload_to = 'static/images/shop/', default = 'static/images/shop/money.jpg')
    price = models.IntegerField()
    last_price = models.IntegerField()

    def __str__(self):
        return "Item ID: {} , Title: {}".format(self.item_id, self.title)

###########################################################################################################
class City(models.Model):
    province = models.CharField(max_length=128, blank=True, default='')
    city = models.CharField(max_length=128, blank=True, default='')

    def str(self):
        return self.city