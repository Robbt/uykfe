
from os import environ, getcwd
from os.path import join

from uykfe.support.config import CONFIG_ENVDIR

TEST_DIR=join(environ.get(CONFIG_ENVDIR, getcwd()), '.test')
