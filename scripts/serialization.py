import pandas as pd
df = pd.DataFrame({'text': [str(i % 1000) for i in range(1000000)],
                   'numbers': range(1000000)})

import pickle
import cPickle
import json
from functools import partial
from time import time


def timeit(func, n=5):
    start = time()
    for i in range(n):
        func()
    end = time()
    return (end - start) / n


def csvdumps(s):
    s.to_csv('foo')
    return 'foo'

def csvloads(fn):
    return pd.read_csv(fn)

def hdfdumps(s):
    s.to_hdf('foo', 'bar', mode='w')
    return ('foo', 'bar')

def hdfloads(path):
    return pd.read_hdf('foo', 'bar')

def jsonloads(text):
    index, values = json.loads(text)
    return pd.Series(values, index=index)


keys = ['json-no-index', 'json', 'pickle', 'pickle-p2', 'cPickle', 'cPickle-p2', 'msgpack', 'csv', 'hdfstore']

d = {'pickle': [pickle.loads, pickle.dumps],
     'cPickle': [cPickle.loads, cPickle.dumps],
     'pickle-p2': [pickle.loads, partial(pickle.dumps, protocol=2)],
     'cPickle-p2': [cPickle.loads, partial(cPickle.dumps, protocol=2)],
     'msgpack': [pd.read_msgpack, pd.Series.to_msgpack],
     'csv': [csvloads, csvdumps],
     'hdfstore': [hdfloads, hdfdumps],
     'json-no-index': [json.loads, lambda x: json.dumps(list(x))],
     'json': [jsonloads, lambda x: json.dumps([list(x.index), list(x)])]}


result = dict()
for name, (loads, dumps) in d.items():
    text = dumps(df.text)
    numbers = dumps(df.numbers)
    result[name] = {'text': {'dumps': timeit(lambda: dumps(df.text)),
                             'loads': timeit(lambda: loads(text))},
                 'numbers': {'dumps': timeit(lambda: dumps(df.numbers)),
                             'loads': timeit(lambda: loads(numbers))}}

########
# Plot #
########

# Much of this was taken from
# http://nbviewer.ipython.org/gist/mwaskom/886b4e5cb55fed35213d
# by Michael Waskom

import matplotlib.pyplot as plt
import seaborn as sns
sns.set(style="whitegrid", font_scale=1.3)

w, h = 7, 7
f, (left, right) = plt.subplots(nrows=1, ncols=2, sharex=True, figsize=(w*2, h), squeeze=True)

df = pd.DataFrame({'loads': [result[key]['text']['loads'] for key in keys],
                   'dumps': [result[key]['text']['dumps'] for key in keys],
                   'storage': keys})
df = pd.melt(df, "storage", value_name="duration", var_name="operation")

sns.barplot("duration", "storage", "operation", data=df, ax=left)
left.set(xlabel="Duration (s)", ylabel="")
sns.despine(bottom=True)
left.set_title('Cost to Serialize Text')
left.legend(loc="lower center", ncol=2, frameon=True, title="operation")

df = pd.DataFrame({'loads': [result[key]['numbers']['loads'] for key in keys],
                   'dumps': [result[key]['numbers']['dumps'] for key in keys],
                   'storage': keys})
df = pd.melt(df, "storage", value_name="duration", var_name="operation")

sns.barplot("duration", "storage", "operation", data=df, ax=right)
right.set(xlabel="Duration (s)", ylabel="")
sns.despine(bottom=True)
right.set_title('Cost to Serialize Numerical Data')
right.legend(loc="lower center", ncol=2, frameon=True, title="operation")

plt.savefig('../images/serialize.png')

f, ax = plt.subplots(nrows=1, ncols=1, sharex=True, figsize=(w, h), squeeze=True)
keys2 = ['pickle-p2', 'cPickle-p2', 'msgpack', 'hdfstore']
df = pd.DataFrame({'loads': [result[key]['numbers']['loads'] for key in keys2],
                   'dumps': [result[key]['numbers']['dumps'] for key in keys2],
                   'storage': keys2})
df = pd.melt(df, "storage", value_name="duration", var_name="operation")

sns.barplot("duration", "storage", "operation", data=df, ax=ax)
ax.set(xlabel="Duration (s)", ylabel="")
sns.despine(bottom=True)
ax.set_title('Cost to Serialize Numerical Data')
ax.legend(loc="lower center", ncol=2, frameon=True, title="operation")
plt.savefig('../images/serialize-subset.png')


df = pd.DataFrame({'loads': [result[key]['text']['loads'] for key in keys],
                   'dumps': [result[key]['text']['dumps'] for key in keys],
                   'storage': keys})
df2 = df.copy()
start = time()
df2['text'] = df2['text'].astype('category')
end = time()

categories = {'convert': end - start,
              'text': timeit(lambda: cPickle.loads(cPickle.dumps(df.text, protocol=2))),
              'categories': timeit(lambda: cPickle.loads(cPickle.dumps(df2.text, protocol=2)))}

print pd.DataFrame(pd.Series(categories, name='seconds', index=['text', 'convert', 'categories'])).to_html()
plt.show()
