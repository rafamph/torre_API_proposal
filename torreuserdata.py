import requests
import json
from numpy import percentile
from numpy.random import rand
import time, random
from scipy.stats import percentileofscore


def show_common_features(user_group):
    repeated_features = []
    summary = {}

    for user in user_group:
      for feature in [*[*user.values()][0].keys()]:
        repeated_features.append(feature)

    unique_features = list(set(repeated_features))

    for feature in unique_features:
      summary[feature] = repeated_features.count(feature) / len(user_group)

    return summary

#Define a method for keeping only the user profile features we consider relevant
def filter_features(user_group, features):
  return dict((k, user_group[k]) for k in features)

class Data():
    def __init__(self, username, limit=6):
        self.username = username
        self.limit = limit
        self.url = ("https://torre.bio/api/people/%s/network?[deep=%s]" % (username, limit))
        self.headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}



    def find_summary(self):
        response = requests.get(self.url, headers = self.headers)
        people_by_connection = response.json()["graph"]["nodes"]
        all_ids = {}

        for people in people_by_connection:
          try:
            all_ids[people["metadata"]["publicId"]] = people["metadata"]["weight"]
          except:
            pass

        non_zero_users = { k: all_ids[k] for k,v in all_ids.items() if v >= 2}
        scores = list(non_zero_users.values())
        scores.remove(max(scores))

        quartiles = percentile(scores, [25, 50, 75, 90, 95, 99])
        score_min, score_max = min(scores), max(scores)
        all_users = { k: all_ids[k] for k,v in all_ids.items() if v >= score_min }
        list_of_users = list(all_users)

        features_all_users = []
        i = 0
        aprox_time = len(list_of_users)
        for userID in list_of_users:
          url2 = ("https://torre.bio/api/bios/%s" % (userID))
          i += 1
          response2 = requests.get(url2, headers=self.headers)
          features_all_users.append(response2)
          time.sleep(1)
          updated_time = time.strftime('%H:%M:%S', time.gmtime(aprox_time - i))
          print("aprox time :" + str(updated_time))

        user_and_features = {}

        for user in features_all_users:
         tmp_dict = {}
         name = user.json()["person"]["name"]
         for feature in user.json().keys():
             if feature == "person":
               subfeatures = [*user.json()["person"].keys()]
               for subfeature in subfeatures:
                 results = (user.json()["person"][subfeature])
                 if isinstance(results,float) or isinstance(results,bool) or isinstance(results,int):
                   tmp_dict[subfeature] = results
                 elif isinstance(results,dict):
                   for sub_results in [*results.keys()]:
                     if isinstance(results[sub_results],float) or isinstance(results[sub_results],bool) or isinstance(results[sub_results],int):
                       tmp_dict[sub_results] = results[sub_results]
                 else:
                   pass
             elif feature == "stats":
               subfeatures = [*user.json()["stats"].keys()]
               for subfeature in subfeatures:
                 results = (user.json()["stats"][subfeature])
                 if isinstance(results,float) or isinstance(results,bool) or isinstance(results,int):
                   tmp_dict[subfeature] = results
                 else:
                   pass
             elif feature == "languages":
               languages_spoken = len(user.json()["languages"])
               tmp_dict["languages_spoken"] = languages_spoken

         user_and_features[name] = tmp_dict

        Q1 = []
        Q2 = []
        P90 = []
        P95 = []
        P99 = []

        for user in user_and_features.keys():
          if (user_and_features[user]["weight"]) <= quartiles[0]:
            Q1.append({user: user_and_features[user]})
          elif (user_and_features[user]["weight"]) > quartiles[1] and (user_and_features[user]["weight"]) <= quartiles[2]:
            Q2.append({user: user_and_features[user]})
          elif (user_and_features[user]["weight"]) > quartiles[2] and (user_and_features[user]["weight"]) <= quartiles[3]:
            P90.append({user: user_and_features[user]})
          elif (user_and_features[user]["weight"]) > quartiles[3] and (user_and_features[user]["weight"]) <= quartiles[4]:
            P95.append({user: user_and_features[user]})
          else:
            P99.append({user: user_and_features[user]})


        #Filter our relevant attributes for different segments (as we mentioned based on profile weight)
        all_summaries = {}
        features_to_filter = ('publications', 'jobs', 'education', 'projects', 'achievements', 'interests')

        Q1_summary = (show_common_features(Q1))
        Q1_summary = filter_features(Q1_summary, features_to_filter)
        all_summaries["Q1_summary"] = Q1_summary

        Q2_summary = (show_common_features(Q2))
        Q2_summary = filter_features(Q2_summary, features_to_filter)
        all_summaries["Q2_summary"] = Q2_summary

        P90_summary = (show_common_features(P90))
        P90_summary = filter_features(P90_summary, features_to_filter)
        all_summaries["P90_summary"] = P90_summary

        P95_summary = (show_common_features(P95))
        P95_summary = filter_features(P95_summary, features_to_filter)
        all_summaries["P95_summary"] = P95_summary

        P99_summary = (show_common_features(P99))
        P99_summary = filter_features(P99_summary, features_to_filter)
        all_summaries["P99_summary"] = P99_summary


        return all_summaries
