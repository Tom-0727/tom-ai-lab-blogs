/* global hexo */

'use strict';

const path = require('path');

hexo.extend.filter.register('theme_inject', function(injects) {
  injects.head.file('seo-structured-data', path.join(hexo.base_dir, 'templates/seo.ejs'));
});
