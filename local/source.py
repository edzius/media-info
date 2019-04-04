
import re


def matchFileExt(value):
    if len(value) < 3 or len(value) > 4:
        return
    ret = re.match("^(mkv|avi|mp4)$", value, re.I)
    if ret:
        return ret.group(1)

def matchLanguage(value):
    if len(value) < 2 or len(value) > 3:
        return
    ret = re.match("^(LT|EN|RU)", value, re.I)
    if ret:
        return ret.group(1)

def matchSubtitres(value):
    ret = re.match("([A-Z]*sub)", value, re.I)
    if ret:
        return ret.group(1)

def matchYear(value):
    ret = re.match("^\(?(\d\d\d\d)\)?$", value)
    if ret:
        return int(ret.group(1))

def matchCoding(value):
    ret = re.match("^(x264|h264|web\-?rip|web\-?dl|web\-?dlrip|dvd\-?rip|b[dr]\-?rip|hd\-?rip|hdtv|720p|1080p|avc|aac|ac3|dts|divx|xvid|bluray)$", value, re.I)
    if ret:
        return int(ret.group(1))

def matchSeason(value):
    ret = re.match("^S(\d+)", value, re.I)
    if ret:
        return int(ret.group(1))

def matchEpisode(value):
    ret = re.match("E(\d+)$", value, re.I)
    if ret:
        return int(ret.group(1))

def cleanPrefixes(name):
    result = re.match("[\[\(\{][^\]\)\}]*[\]\)\}](.*)", name)
    if result:
        return result.group(1)
    return name

def swapTitle(line, length):
    while length < len(line):
        if re.match("[ \.\-_]", line[length]):
            break
        length += 1

    title = line[:length]
    title = re.sub(r"(\w{3,})[\._]", r"\1 ", title)
    title = re.sub(r"(\w{2}[\._])", r"\1 ", title)
    title = re.sub(r"(\w{1}\.)(\w{2,})", r"\1 \2", title)
    return title

def processName(name):
    if not name:
        return

    name = cleanPrefixes(name)
    arr = re.split("[ \.\-_]", name)
    idx = len(arr)
    lastid = None

    ret = {}
    ret['type'] = 'movie'
    for val in reversed(arr):
        idx -= 1
        ext = matchFileExt(val)
        lang = matchLanguage(val)
        subs = matchSubtitres(val)
        year = matchYear(val)
        code = matchCoding(val)
        season = matchSeason(val)
        episode = matchEpisode(val)

        if 'ext' not in ret and ext:
            ret['ext'] = ext
            lastId = idx
        if lang:
            ret['lang'] = ret['lang'] or []
            ret['lang'].append(lang)
            lastId = idx
        if subs:
            ret['subs'] = ret['subs'] or []
            ret['subs'].append(subs)
            lastId = idx
        if 'year' not in ret and year:
            ret['year'] = year
            lastId = idx
        if code:
            ret['code'] = ret['code'] or []
            ret['code'].append(code)
            lastId = idx
        if 'season' not in ret and season:
            ret['season'] = season
            ret['type'] = 'episode'
            lastId = idx
        if 'episode' not in ret and episode:
            ret['episode'] = episode
            ret['type'] = 'episode'
            lastId = idx

    if lastId != None:
        ret['title'] = swapTitle(name, len(' '.join(arr[:lastId]).strip()))
        return ret


def processDirName(path):
    parts = path.split('/')
    if len(parts) < 2:
        return;

    return processName(parts[-2])

def processFileName(path):
    parts = path.split('/')

    return processName(parts[-1])

def modContractionsGeneric(title):
    #return title.replace(/((?<=\bi)m|(?<=\b(you|they))re|(?<=\b(he|she|it))s|(?<=\b(wasn|weren|won))t|(?<=\b(i|you|they))ll|(?<=\b(i|you|we))ve)\b/gi, '\'$1');
    title = re.sub(r"\b(isn|hasn|hadn|didn|wouldn|can|won|wasn|weren)t\b", r"\1't", title, flags=re.I)
    title = re.sub(r"\b(she|there|he|it|who)s\b", r"\1's", title, flags=re.I)
    title = re.sub(r"\bim\b", r"i'm", title, flags=re.I)
    title = re.sub(r"\b(i|you|they)ll\b", r"\1'll", title, flags=re.I) # we'll, she'll
    title = re.sub(r"\b(i|you|she|we|they)d\b", r"\1'd", title, flags=re.I)
    title = re.sub(r"\b(i|you|we|they)ve\b", r"\1've", title, flags=re.I)
    title = re.sub(r"\b(you|they)re\b", r"\1're", title, flags=re.I) # we're
    return title

def modContractionsWere(title):
    #return title.replace(/((?<=\bwe)re)\b/gi, '\'$1')
    return re.sub(r"\bwere\b", r"we're", title, flags=re.I)

def modPossesiveSingular(title):
    return re.sub(r"^(\S*)s\b", r"$1's", title, count=1, flags=re.I)

def modPossesivePlural(title):
    return re.sub("^(\S*)s\b", "$1s'", title, flags=re.I)
