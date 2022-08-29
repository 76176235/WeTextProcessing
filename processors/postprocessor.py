# Copyright (c) 2022 Zhendong Peng (pzd17@tsinghua.org.cn)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from processors.processor import Processor

from pynini import cdrewrite, difference, string_file
from pynini.lib.pynutil import delete, insert


class PostProcessor(Processor):

    def __init__(self,
                 remove_puncts=False,
                 to_upper=False,
                 to_lower=False,
                 tag_oov=False):
        super().__init__(name='postprocessor')
        puncts = string_file('data/char/punctuations_zh.tsv')
        lower2upper = string_file('data/char/lower2upper.tsv')
        upper2lower = string_file('data/char/upper2lower.tsv')
        zh_charset_std = string_file(
            'data/char/charset_national_standard_2013_8105.tsv')
        zh_charset_ext = string_file('data/char/charset_extension.tsv')

        processor = cdrewrite('', '', '', self.VSIGMA)
        if remove_puncts:
            processor @= cdrewrite(delete(puncts | self.PUNCT), '', '',
                                   self.VSIGMA)

        if to_upper:
            processor @= cdrewrite(lower2upper, '', '', self.VSIGMA)
        if to_lower:
            processor @= cdrewrite(upper2lower, '', '', self.VSIGMA)

        if tag_oov:
            charset = (zh_charset_std | zh_charset_ext | puncts | self.DIGIT
                       | self.ALPHA | self.PUNCT | self.SPACE)
            with open('data/char/oov_tags.tsv') as f:
                tags = f.readline().strip().split('\t')
                assert len(tags) == 2
                ltag, rtag = tags
            tag_oov = (insert(ltag) + difference(self.VCHAR, charset) +
                       insert(rtag))
            processor @= cdrewrite(tag_oov, '', '', self.VSIGMA)

        self.processor = processor.optimize()
