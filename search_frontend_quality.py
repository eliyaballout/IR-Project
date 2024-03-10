from flask import Flask, request, jsonify
from nltk.stem.porter import PorterStemmer
from inverted_index import InvertedIndex
import os
import json
from backend import *
import nltk
from nltk.corpus import stopwords
import time


nltk.download('stopwords')



#######################################################################################################################
################################################ MyFlaskApp Class #####################################################


class MyFlaskApp(Flask):
  def run(self, host=None, port=None, debug=None, **options):
    super(MyFlaskApp, self).run(host=host, port=port, debug=debug, **options)



#######################################################################################################################
################################################# Initializations #####################################################

# --- Bucket name --- #
BUCKET_NAME = "ir_project__bucket1"


# tokenizer and stopwords
english_stopwords = frozenset(stopwords.words('english'))
corpus_stopwords = ["category", "references", "also", "external", "links", 
                    "may", "first", "see", "history", "people", "one", "two", 
                    "part", "thumb", "including", "second", "following", 
                    "many", "however", "would", "became"]

all_stopwords = english_stopwords.union(corpus_stopwords)
RE_WORD = re.compile(r"""[\#\@\w](['\-]?\w){2,24}""", re.UNICODE)

# stemmer
ps = PorterStemmer()


app = MyFlaskApp(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False


# download all indexes
body_inv_index = InvertedIndex.read_index('body', 'body_index', BUCKET_NAME)
title_inv_index = InvertedIndex.read_index('title', 'title_index', BUCKET_NAME)
anchor_inv_index = InvertedIndex.read_index('anchor', 'anchor_index', BUCKET_NAME)


# download page rank to pr variable
os.system(f"gsutil cp gs://{BUCKET_NAME}/pr/pr.json .")
with open('pr.json') as prJSON:
  pr = json.load(prJSON)



# used for calculating different measurements
ideal = {
  "genetics": ["12266", "8406655", "1590357", "4250553", "339838", "7955", "219268", "19595", "12383", "12385", "1763082", "159266", "274192", "3464219", "12562", "22249817", "418605", "6438", "14235691", "24235330", "1483646", "38203371", "403627", "12437", "30860403", "13457", "12388", "12796", "68300", "310782", "2839975", "1911", "19702", "4087965", "364423", "9737", "583438", "155624", "72016", "49033", "155192", "4816754", "480107", "604020", "158005", "9236"], 
  "Who is considered the \"Father of the United States\"?": ["540802", "519482", "260899", "21816397", "223202", "15124855", "261175", "1226966", "432330", "193877", "260870", "547346", "230108", "75958", "1149544", "93561", "260875", "233146", "2057489", "560404", "24905", "260898", "105892", "31171", "260873", "573097", "260910", "51591978", "261172", "427815", "261170", "21828607", "10133", "1337709", "261187", "25068298", "559128", "261182", "230337", "33299", "261168", "261185", "1943659", "27057637", "261178", "266907", "242102", "1201169", "152055", "261186"], 
  "economic": ["9223", "6639133", "692262", "148131", "69415", "380845", "370432", "23573352", "5416", "32022", "45633", "25382", "19280607", "57349", "48852", "788900", "638834", "4095185", "503119", "10517", "241232", "6801189", "17326", "19283335", "12083679", "1352048", "38289", "12594", "181293", "9942688", "216664", "7843", "2061965", "72529", "210522", "177512", "46044", "227630", "139993", "19284336", "3484684", "916345", "19337279", "2236116", "33853117", "172185", "411315", "19804420", "50145", "177698"], 
  "When was the United Nations founded?": ["31769", "1157540", "88805", "188955", "9300546", "31969", "31957", "1341065", "335057", "216034", "8334078", "31956", "54111479", "47955040", "24644042", "37107", "479389", "3218829", "3424435", "6480536", "856769", "17926", "12029262", "36587", "50883", "3054918", "640822", "325572", "32315", "2157983", "32268", "24650013", "2959252", "565612", "31899", "32178", "82256", "31958", "19698110", "635790", "31904", "36480350", "162410", "31959", "1157544", "1406618"], 
  "video gaming": ["5363", "32401", "564204", "372478", "32629", "64483771", "182053", "4373654", "10918530", "2538794", "41011935", "356777", "8052761", "41568624", "44542278", "31669618", "16000063", "11762000", "565944", "41773358", "598395", "67378620", "700265", "19992532", "25395149", "490610", "43758363", "26757970", "1617333", "474398", "1336512", "61909134", "2292497", "46666400", "14199", "38062234", "7763396", "19220448", "170581", "32399", "485939", "1910313", "17166020", "3382456", "13392949", "2742821"], 
  "3D printing technology": ["1305947", "53292993", "53292889", "38673321", "1086236", "62452729", "62443231", "44215035", "45719282", "35742703", "31260053", "53844351", "3160379", "4234010", "62313405", "43643043", "41615704", "52904006", "56543723", "29017963", "1993025", "48160815", "62442607", "63513865", "19653871", "58490571", "19986879", "67944537", "43351996", "66703721", "38430022", "23760854", "53527471", "841755", "58504805", "35194697", "28971287", "24497031", "43475529", "44858650", "44314961", "40891179", "26610144", "43912217"], 
  "Who is the author of \"1984\"?": ["23454753", "11891", "19245926", "4261", "14254136", "22281825", "6069806", "61174690", "683456", "65016998", "2360464", "190220", "53626279", "19559447", "19389306", "155736", "279716", "46265278", "620", "65257079", "80562", "15302849", "15927", "20781912", "23008930", "36681", "842197", "234555", "38114", "24713721", "1978747", "1685538", "1483304", "3287555", "21725", "1942881", "1151272", "28927061", "25059564", "1895332", "3434631", "152265", "2775435", "30761"], 
  "bioinformatics": ["4214", "363695", "53970843", "24738960", "235550", "37670240", "475160", "149289", "22155527", "38542005", "917460", "10221795", "41282920", "58885019", "14673667", "2056296", "8634376", "25474825", "24393120"], 
  "Who is known for proposing the heliocentric model of the solar system?": ["244588", "8837050", "2748665", "323592", "74857", "3362809", "60325936", "35223708", "7327", "83754", "1028515", "276857", "29688374", "252372", "19327051", "62137449", "30027", "15736", "25998318", "50650", "18352021", "17553", "17052696", "12963", "31880", "14021", "10385519", "60549", "58939", "3194945", "628083", "2639335", "659190", "878461", "1864889", "206542", "4536514", "13758", "14400", "383129", "4385475", "899973", "143608", "208656", "26700"], 
  "Describe the process of water erosion.": ["9696", "4372011", "59416", "11397380", "149261", "4400374", "5077608", "2818161", "1157585", "643020", "26277662", "15841377", "949526", "3882879", "6319149", "200167", "439282", "4895120", "72585", "5573115", "49012757", "8113846", "37755119", "3159833", "3198788", "17110306", "286837", "67251594", "78481", "47741580", "52921836", "21950720", "273997", "60343", "40548511", "1018637", "6025205", "4132010", "307279", "13440971", "186193", "7999492", "69442", "13435", "54840", "406430", "56462624", "33306"], 
  "When was the Berlin Wall constructed?": ["3722", "61917089", "33170", "29696068", "9483", "18360765", "200989", "53816420", "849186", "30257891", "32842267", "24815929", "156604", "5072312", "13058", "24790125", "24597", "2697626", "24806372", "54286150", "5261273", "18953051", "370681", "716962", "40035819", "48322587", "38347242", "3354", "24448273", "5155986", "75251", "48217040", "261678", "61103", "36501294", "67325752", "27599353", "24813045", "242099", "900258", "14061140", "947625", "898673", "8925150", "44353520", "36939655", "21936384", "2511", "58548"], 
  "What is the meaning of the term \"Habeas Corpus\"?": ["14091", "8758045", "1123587", "3972844", "23693473", "9893745", "12012887", "32164513", "27348709", "47898402", "43030290", "25590696", "10011240", "8613452", "11660500", "37423356", "1043779", "10133224", "600901", "1378513", "50229592", "10715952", "15629894", "25584694", "1352158", "16751609", "55207856", "158492", "26565511", "13399040", "627536", "2890244", "1123174", "31646", "23545213", "7201014", "146275", "37064", "14649174", "146274", "22957370", "1713578", "36733574", "40359", "642925", "62723245", "551210", "2090028", "38867"], 
  "telecommunications": ["33094374", "46545", "928324", "7531293", "620113", "27452465", "41782", "1145887", "30003", "53738", "3276921", "19752979", "8774050", "12808", "2112491", "45207", "17912042", "1338556", "196010", "21347591", "26668156", "4094802", "14836", "47005", "18619278", "66040"], 
  "internet": ["14539", "13692", "300602", "33789688", "100245", "15323", "12057519", "15215", "63973", "3686796", "48402", "15172", "33139", "147184", "176931", "15285", "19776474", "827154", "15476", "17885119", "14742", "1088227", "856845", "429909", "294813", "11207736", "1569607", "14594", "84022", "14730", "1616492", "769088", "15236", "15734720", "203466", "396223", "41173164", "597727", "11056386", "1398166", "286013", "11357820"], 
  "What are the characteristics of a chemical element?": ["5659", "2152181", "23053", "9722260", "5180", "42209150", "86350", "199079", "619795", "7043", "21347411", "902", "901", "181556", "673", "77473", "13884326", "18899", "86347", "30047", "85425", "19916", "9478", "9479", "13466", "3756", "30043", "77474", "19042", "60088", "896", "13764", "27117", "13255", "27116", "2231059", "10624594", "13256", "67611", "14750", "5667", "30042", "62200", "12242", "102193", "30046", "6271", "68326", "23055", "19600416"], 
  "Describe the structure of a plant cell.": ["23977", "6312", "13932032", "6355", "32347", "4230", "33051527", "2049869", "22393", "2959657", "1814677", "5184", "7555884", "5106530", "5134478", "6235", "483108", "18952693", "32572", "227682", "9775", "6227883", "6781", "103915", "21958", "46675", "61899", "9927", "7556348", "14464979", "18973622", "156970", "153522", "656613", "24544", "6911", "200182", "21514323", "6339", "20639545", "19828134", "32624519", "19588", "24536543", "25766", "747128", "21076226", "2784383", "102858"], 
  "Who painted \"Starry Night\"?": ["1115370", "1878689", "32603", "62143846", "1883522", "43603948", "32520576", "7529015", "31591527", "4185877", "6176363", "34490285", "17471799", "66797719", "1352611", "9779", "36809948", "11064758", "6249860", "31298340", "34933345", "745523", "2686178", "20050190", "1480900", "49600865", "9988530", "31625863", "45567743", "6337562", "58987216", "27773473", "63051424"], 
  "computer": ["7878457", "18457137", "5323", "21808348", "7677", "5783", "198584", "249402", "375416", "6596", "18994196", "3833695", "5311", "50408", "4122592", "25652303", "2428", "5300", "3879451", "7056", "5213", "20266", "4182449", "22194", "6806", "7398", "7077", "25122906", "37153", "18567210", "5309", "25220", "31626763", "68181", "18890", "6010", "64750", "23534602", "37315", "323392", "54427", "23659805", "81196", "328784", "194424", "10429990"], 
  "What is the structure of the Earth's layers?": ["1417149", "1705831", "2939202", "1079771", "9228", "146249", "59623952", "5593595", "45241275", "145716", "145700", "61044116", "145717", "1079866", "202898", "673768", "1589335", "1431559", "24944", "202899", "78490", "981252", "3406503", "47460", "41077022", "494100", "864017", "59601438", "673743", "58614271", "5555728", "47454", "11107751", "41822", "145813", "375826", "8307722", "15097", "254452", "54962", "11603215", "2068726", "7604906", "44412"], 
  "When did World War II end?": ["32927", "360422", "16555042", "34624", "215257", "390508", "16554434", "1880615", "2198844", "11237483", "1393850", "4653534", "16554523", "16554637", "142735", "16554947", "21212", "16554732", "14471451", "1373357", "40705030", "2395137", "16554826", "6513604", "519489", "342641", "1285991", "365519", "261678", "291145", "21619085", "519516", "4008941", "87995", "20854645", "765642", "7062377", "240900", "900011", "202102", "350111", "493696", "64507858", "342640", "228080", "1467679", "1168996", "42685705", "39743540", "637072"], 
  "When was the Gutenberg printing press invented?": ["23295", "15745", "7695885", "11012076", "47300", "255041", "44723", "286327", "18723", "662134", "1591936", "23036", "5843862", "20218892", "3277654", "142743", "7643744", "275989", "33040421", "36707999", "11502064", "67033930", "21436856", "16688458", "21499093", "14029854", "3672187", "28679509", "35746798", "43577463", "3626755", "1041702", "7458233", "24171677", "1857103", "1619933", "23301", "269903", "52677530", "67548191", "23487645", "12798398", "42438345", "4688539", "25739212", "666391"], 
  "medicine": ["18957", "180121", "428966", "1580383", "14194", "9311172", "3172179", "293885", "205264", "10013", "1845", "23315", "52502", "381552", "457857", "5827094", "310484", "52671", "12039054", "13486", "304263", "212698", "236674", "439973", "5992", "199884", "1032780", "1479393", "261925", "1656748", "431259", "2285007", "1043627", "408290", "1119701", "3552463", "52974", "347838", "175440", "2106879", "2584146", "299014", "32654", "2245783", "2652481"], 
  "Describe the water cycle.": ["200167", "59586681", "13435", "33306", "67695754", "23972610", "398638", "4638936", "1858623", "47521", "89547", "78481", "145753", "56024424", "7995309", "5565588", "4687085", "18952860", "4400374", "10303", "62557527", "19009110", "286260", "922554", "18581463", "6262231", "4446652", "3159833", "18842359", "2465480", "18842395", "4224324", "18077896", "262927", "316612", "28191", "17673401", "2880847", "18842323", "18842308", "47503", "30718", "14946", "102024", "5095558", "11717197", "1715797"], 
  "artificial intelligence": ["1164", "142224", "2894560", "15893057", "52588198", "6585513", "54245", "21523", "586357", "50336055", "566680", "48795986", "60639760", "41755648", "5841092", "233488", "726659", "16598232", "1654769", "813176", "2958015", "12413470", "308362", "54575571", "54008163", "21391751", "13659583", "339417", "32472154", "22264262", "63451675", "11746227", "59539440", "19639", "3548574", "41873354", "534794", "63225340", "2846", "15874732", "46583121", "434274", "7872324"], 
  "physics": ["22939", "22688097", "13758", "19594028", "24489", "5387", "1692795", "102847", "24236", "23269", "26998617", "844186", "149861", "52497", "151066", "21285", "173416", "740540", "25916521", "25202", "23259", "19595664", "2641938", "950012", "36626070", "183089", "2796131", "685311", "1200", "312881", "278366", "4063091", "10279126", "18698687", "1506216", "106418", "405493", "168907", "4769321", "358381", "19679192", "1453385", "2711029", "123450", "25523", "736"], 
  "nanotechnology": ["21488", "7064233", "38324933", "21514", "19637", "14431229", "1006597", "1234517", "2154572", "868108", "60011838", "60786392", "26901564", "28054293", "32249901", "7067473", "2104510", "31746484", "21561", "6736363", "10004859", "63399479", "8674917", "7200558", "905278", "8327305", "19079770", "16065393", "20234388", "1032221", "10209776", "336994", "175996", "64485122", "55566398", "5320", "63888621", "18069384", "56007469", "9548739", "4647936", "3602968", "33661741", "30380229", "19486733", "44158633", "7075936"], 
  "When did the Black Death pandemic occur?": ["4501", "16392927", "20993417", "33390780", "20155274", "63929030", "1543486", "4807194", "12286", "945818", "63928828", "33390747", "63929142", "55743836", "36692538", "20155412", "4746", "63956954", "548536", "17503394", "54426991", "1930322", "68025111", "63958425", "35316091", "63956701", "24255", "3573933", "60502984", "986", "1923607", "66291781", "63377663", "5871318", "63382758", "845862", "1777327", "34367", "66426779", "68082858", "63360170", "71054", "19937260", "63365925", "55586589", "529280", "63411128"], 
  "neuroscience": ["21245", "50326", "665536", "277956", "1305044", "58361969", "4794482", "271430", "605477", "20515023", "2640086", "21226", "1948637", "3354877", "1555376", "26081918", "3839716", "25049383", "59255005", "5212945", "24646984", "1822196", "25935238", "36563803", "12101207", "2208074", "3811045", "762064", "44135823", "42003951", "17935654", "25225295", "59161036", "542377", "34095626", "515094", "16264786", "20848680", "26565579", "47403822", "703002", "47095270", "3975854", "1937595", "1391133", "25829369", "27024757"], 
  "snowboard": ["38957", "28262", "25855820", "13006860", "25189611", "2382902", "5882291", "39129987", "175281", "18251011", "21219884", "12808675", "4170732", "3971307", "1173744", "47808636"], 
  "Who is the founder of modern psychology?": ["1573230", "34128", "90682", "3129664", "26743", "912656", "22921", "42031", "91452", "203499", "981440", "27092290", "12385964", "1976138", "81590", "23663950", "4868", "199877", "5507074", "36921977", "237253", "61705026", "364299", "95274", "518927", "23572093", "2405481", "13647", "31711387", "42037", "23585", "326313", "301882", "13512823", "84864", "9014", "70402", "317501", "4419426", "324180", "448370", "25306680", "20927655", "41358018", "932831", "3959877", "37205195", "248799", "58741718"]
}



#######################################################################################################################
################################################### search function ###################################################


# funciton get_results used in search from search_frontend.py
def get_results(query, body_weight, title_weight, anchor_weight, pr_weight):

  # get tokens
  query_tokens = [token.group() for token in RE_WORD.finditer(query.lower())]
  query_tokens = [token for token in query_tokens if token not in all_stopwords]

  # get body results
  body_results = dict(get_body_tfidf_score(query, body_inv_index, 100))


  # get title results
  docs_and_scores_title = {}

  stems = []
  for token in query_tokens:
    stems.append(ps.stem(token))

  for token in stems:
    docs_and_tfs = title_inv_index.read_posting_list(token, 'title', BUCKET_NAME)
    for (doc,tf) in docs_and_tfs:
        if doc not in docs_and_scores_title.keys():
          docs_and_scores_title[doc] = 1 / len(stems)
        else:
          docs_and_scores_title[doc] = docs_and_scores_title[doc] + (1 / len(stems))
  docs_and_scores_title_list = [(k, v) for k, v in docs_and_scores_title.items()]
  title_results = dict(sorted(docs_and_scores_title_list, key = lambda x: x[1],reverse=True)[:100])

  # get anchor results
  docs_and_scores_anchor = {}
  for token in query_tokens:
    docs_and_tfs = anchor_inv_index.read_posting_list(token, 'anchor', BUCKET_NAME)
    for (doc,tf) in docs_and_tfs:
        if doc not in docs_and_scores_anchor.keys():
          docs_and_scores_anchor[doc] = 1 / len(query_tokens)
        else:
          docs_and_scores_anchor[doc] = docs_and_scores_anchor[doc] + (1 / len(query_tokens))
  docs_and_scores_anchor_list = [(k, v) for k, v in docs_and_scores_anchor.items()]
  anchor_results = dict(sorted(docs_and_scores_anchor_list, key = lambda x: x[1],reverse=True)[:100])

  # all candidates
  all_candidate_docs = set(list(body_results.keys()) + list(title_results.keys()) + list(anchor_results.keys()))

  #searching
  docs_and_scores_final = dict()
  # calculate variables used in searching
  max_body = 1
  if body_results.values():
    max_body = max(body_results.values())

  max_title = 1
  if title_results.values():
    max_title = max(title_results.values())

  max_anchor = 1
  if anchor_results.values():
    max_anchor = max(anchor_results.values())

  prs = []
  for doc in all_candidate_docs:
    if(str(doc) in pr.keys()):
      prs.append(pr[str(doc)])

  max_pr = max(prs)

  # give score for each doc
  for doc in all_candidate_docs:
    body_score = 0
    title_score = 0
    anchor_score = 0
    pr_score = 0

    if(doc in body_results.keys()):
      body_score = body_weight * (body_results[doc]/max_body)

    if(doc in title_results.keys()):
      title_score = title_weight * (title_results[doc]/max_title)

    if(doc in anchor_results.keys()):
      anchor_score = anchor_weight * (anchor_results[doc]/max_anchor)
    
    if(str(doc) in pr.keys()):
      pr_score = pr_weight * (pr[str(doc)]/max_pr)
      
    docs_and_scores_final[doc] = body_score + title_score + anchor_score + pr_score

  res = sorted(list(docs_and_scores_final.items()), key=lambda x: x[1], reverse=True)[:100]
  return list(map(lambda x: str(x[0]), res))



#######################################################################################################################
################################################# measurement functions ###############################################


def average_precision(true_list, predicted_list, k=10):
  true_set = frozenset(true_list)
  predicted_list = predicted_list[:k]
  precisions = []
  for i,doc_id in enumerate(predicted_list):
    if doc_id in true_set:
      prec = (len(precisions)+1) / (i+1)
      precisions.append(prec)
  
  if len(precisions) == 0:
    return 0.0
  
  return round(sum(precisions)/len(precisions),3)


def precision_at_k(true_list, predicted_list, k=10):
  true_set = frozenset(true_list)
  predicted_list = predicted_list[:k]
  if len(predicted_list) == 0:
    return 0.0
  
  return round(len([1 for doc_id in predicted_list if doc_id in true_set]) / len(predicted_list), 3)


def recall_at_k(true_list, predicted_list, k=10):
  true_set = frozenset(true_list)
  predicted_list = predicted_list[:k]
  if len(true_set) < 1:
    return 1.0
  
  return round(len([1 for doc_id in predicted_list if doc_id in true_set]) / len(true_set), 3)


def f1_at_k(true_list, predicted_list, k=30):
  p = precision_at_k(true_list, predicted_list, k)
  r = recall_at_k(true_list, predicted_list, k)
  if p == 0.0 or r == 0.0:
    return 0.0
  
  return round(2.0 / (1.0/p + 1.0/r), 3)


def r_precision(true_list, predicted_list):
  true_set = frozenset(true_list)
  predicted_list = predicted_list[:len(true_list)]
  if len(predicted_list) == 0:
    return 0.0
  
  return round(len([1 for doc_id in predicted_list if doc_id in true_set]) / len(true_list), 3)


#######################################################################################################################
################################################## All Routes #########################################################


@app.route("/search")
def search():
  ''' Returns up to a 100 of your best search results for the query. This is 
    the place to put forward your best search engine, and you are free to
    implement the retrieval whoever you'd like within the bound of the 
    project requirements (efficiency, quality, etc.). That means it is up to
    you to decide on whether to use stemming, remove stopwords, use 
    PageRank, query expansion, etc.

    To issue a query navigate to a URL like:
      http://YOUR_SERVER_DOMAIN/search?query=hello+world
    where YOUR_SERVER_DOMAIN is something like XXXX-XX-XX-XX-XX.ngrok.io
    if you're using ngrok on Colab or your external IP on GCP.
  Returns:
  --------
    list of up to 100 search results, ordered from best to worst where each 
    element is a tuple (wiki_id, title).
  '''

  map10res = []
  recall = []
  precision = []
  rprecision = []
  f1 = []
  times = []

  # iterate through each query and collect measurements
  # change weight to see how it affects the measurements
  for query, true_wids in ideal.items():
    print(query)

    t_start = time.time()
    res = get_results(query, 0.35, 0.35, 0.05, 0.25)
    times.append(time.time() - t_start)
    
    map10res.append(average_precision(true_wids, res))
    recall.append(recall_at_k(true_wids, res))
    precision.append(precision_at_k(true_wids, res))
    rprecision.append(r_precision(true_wids, res))
    f1.append(r_precision(true_wids, res))
    
    
  # get average
  map10 = sum(map10res) / len(map10res)
  recall_score = sum(recall) / len(recall)
  precision_score = sum(precision) / len(precision)
  rprecision_score = sum(rprecision) / len(rprecision)
  f1_30 = sum(f1) / len(f1)
  time_score = sum(times) / len(times)
  

  # print results in console
  print("MAP@10: " + str(map10))
  print("Precision@10: " + str(precision_score))
  print("Recall@10: " + str(recall_score))
  print("R-Precision: " + str(rprecision_score))
  print("F1@30:" + str(f1_30))
  print("avg_time: " + str(time_score))

  res = [map10, precision_score, recall_score, rprecision_score, f1_30, time_score]

  return jsonify(res)



#######################################################################################################################
################################################## Run The App ########################################################


if __name__ == '__main__':
  # run the Flask RESTful API, make the server publicly available (host='0.0.0.0') on port 8080
  app.run(host='0.0.0.0', port=8080, debug=True, use_reloader=False)