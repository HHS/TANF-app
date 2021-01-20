var BrowserDetect = {
	init: function () {
		this.browser = this.searchString(this.dataBrowser) || "An unknown browser";
		this.version = this.searchVersion(navigator.userAgent)
			|| this.searchVersion(navigator.appVersion)
			|| "an unknown version";
		this.OS = this.searchString(this.dataOS) || "an unknown OS";
	},
	searchString: function (data) {
		for (var i=0;i<data.length;i++)	{
			var dataString = data[i].string;
			var dataProp = data[i].prop;
			this.versionSearchString = data[i].versionSearch || data[i].identity;
			if (dataString) {
				if (dataString.indexOf(data[i].subString) != -1)
					return data[i].identity;
			}
			else if (dataProp)
				return data[i].identity;
		}
	},
	searchVersion: function (dataString) {
		var index = dataString.indexOf(this.versionSearchString);
		if (index == -1) return;
		return parseFloat(dataString.substring(index+this.versionSearchString.length+1));
	},
	dataBrowser: [
		{
			string: navigator.userAgent,
			subString: "Chrome",
			identity: "Chrome"
		},
		{ 	string: navigator.userAgent,
			subString: "OmniWeb",
			versionSearch: "OmniWeb/",
			identity: "OmniWeb"
		},
		{
			string: navigator.vendor,
			subString: "Apple",
			identity: "Safari",
			versionSearch: "Version"
		},
		{
			prop: window.opera,
			identity: "Opera",
			versionSearch: "Version"
		},
		{
			string: navigator.vendor,
			subString: "iCab",
			identity: "iCab"
		},
		{
			string: navigator.vendor,
			subString: "KDE",
			identity: "Konqueror"
		},
		{
			string: navigator.userAgent,
			subString: "Firefox",
			identity: "Firefox"
		},
		{
			string: navigator.vendor,
			subString: "Camino",
			identity: "Camino"
		},
		{		// for newer Netscapes (6+)
			string: navigator.userAgent,
			subString: "Netscape",
			identity: "Netscape"
		},
		{
			string: navigator.userAgent,
			subString: "MSIE",
			identity: "Explorer",
			versionSearch: "MSIE"
		},
		{
			string: navigator.userAgent,
			subString: "Gecko",
			identity: "Mozilla",
			versionSearch: "rv"
		},
		{ 		// for older Netscapes (4-)
			string: navigator.userAgent,
			subString: "Mozilla",
			identity: "Netscape",
			versionSearch: "Mozilla"
		}
	],
	dataOS : [
		{
			string: navigator.platform,
			subString: "Win",
			identity: "Windows"
		},
		{
			string: navigator.platform,
			subString: "Mac",
			identity: "Mac"
		},
		{
			   string: navigator.userAgent,
			   subString: "iPhone",
			   identity: "iPhone/iPod"
	    },
		{
			string: navigator.platform,
			subString: "Linux",
			identity: "Linux"
		}
	]

};
BrowserDetect.init();;
(function($,sr){

  // debouncing function from John Hann
  // http://unscriptable.com/index.php/2009/03/20/debouncing-javascript-methods/
  var debounce = function (func, threshold, execAsap) {
      var timeout;

      return function debounced () {
          var obj = this, args = arguments;
          function delayed () {
              if (!execAsap)
                  func.apply(obj, args);
              timeout = null;
          };

          if (timeout)
              clearTimeout(timeout);
          else if (execAsap)
              func.apply(obj, args);

          timeout = setTimeout(delayed, threshold || 100);
      };
  }
  // smartresize 
  jQuery.fn[sr] = function(fn){  return fn ? this.bind('resize', debounce(fn)) : this.trigger(sr); };

})(jQuery,'smartresize');;
var onytplayerStateChange,
  oniframeplayerStateChange;

function onYouTubePlayerReady(playerId) {
  var nid = playerId.match(/youtube(\d+)/i)[1];
  window['player' + nid] = document.getElementById(playerId);
  window['player' + nid].addEventListener("onStateChange", "onytplayerStateChange");
}

function is_touch_device() {
  return 'ontouchstart' in window // works on most browsers
    ||
    'onmsgesturechange' in window; // works on ie10
};

(function($) {

  Drupal.behaviors.acfGeneral = {
    attach: function(context, settings) {

      var resize_eventbrite = function() {
        $('.eventbrite-form').each(function() {
          var $iframe = $(this);
          $iframe.attr('scrolling', 'no');
          var height = ($iframe[0].contentWindow.document.body.scrollHeight) + 11;
          $iframe.height(height);
          $iframe.load(function() {
            var height = ($iframe[0].contentWindow.document.body.scrollHeight) + 11;
            $iframe.height(height);
          });
        });
      };
      resize_eventbrite();
      $(window).smartresize(function() {
        resize_eventbrite();
      });

      $('a.back', context).click(function(e) {
        e.preventDefault();
        parent.history.back();
      });

      $('body.page-office-opre #block-acf-research-library-latest h4.node-title a, .block-acf-research-pages-opre h2.node-title a').attr('target', '_blank');

      $('#featured, #main, #footer-wrapper').find("a[href*='http']:not([href*='" + location.hostname.replace("www.", "") + "']):not([href*='hhs.gov']):not([href*='childwelfare.gov'])").each(function() {
        if ($(this).text() != '' && !$(this).hasClass('no-logo')) {
          $(this).once('external').attr({
            target: '_blank',
            title: ''
          }).after($('<a/>').html($('<span/>').text('Visit disclaimer page').addClass('element-invisible')).attr({
            href: Drupal.settings.basePath + 'disclaimers'
          }).addClass('external')).click(function(e) {
            var url = $(this).context.href;
            if (typeof ga !== 'undefined') {
              ga('send', 'event', 'outbound', 'click', url, {
                'transport': 'beacon',
              });
            }
          });
        }
      });
      $('#block-system-main').find('.image').each(function() {
        var $image = $(this),
          $img = $image.find('img'),
          $caption = $image.find('.caption');
        if ($caption.length) {
          $img.load(function() {
            $image.css('paddingBottom', $caption.innerHeight() + 'px');
          });
        }
      });
      var $breadcrumb = $('#breadcrumb');
      if ($breadcrumb.length) {
        var $print = $('<a/>').text('Print').addClass('print').click(function(e) {
          e.preventDefault();
          window.print();
        });
        $breadcrumb.append($print);
      }
    }
  }

  Drupal.behaviors.acfEyebrowDropdown = {
    attach: function(context, settings) {
      var $breadcrumb = $('#eyebrow-breadcrumb', context),
        $office = $breadcrumb.find('li.office'),
        toggleBranch = function() {
          if ($office.hasClass('hover')) {
            closeBranch();
          } else {
            openBranch();
          }
        },
        openBranch = function() {
          $office.addClass('hover').find('.dropdown').removeClass('element-invisible');
        },
        closeBranch = function() {
          $office.removeClass('hover').find('.dropdown').addClass('element-invisible');
        };

      if (is_touch_device()) {
        $('html').click(function() {
          closeBranch();
        });

        $office.click(function(e) {
          e.stopPropagation();
        });

        $office.children('a').click(function(e) {
          e.preventDefault();
          toggleBranch();
        });
      } else {
        $office.find('a').focus(function() {
          openBranch();
        });
        $office.find('a').blur(function() {
          closeBranch();
        });
        $office.hover(function() {
          openBranch();
        }, function() {
          closeBranch();
        });
      }

    }
  }

  Drupal.behaviors.acfNavigation = {
    attach: function(context, settings) {
      var $links = $('#main-menu-links', context),
        openBranch = function($branch) {
          $branch.addClass('hover').find('.item-list-wrapper').removeClass('element-invisible');
          if ($branch.hasClass('menu-programs') || ($('body').hasClass('page-office-css') && $branch.hasClass('menu-state-agencies'))) {
            var height = 0;
            $branch.find('.menu-program-inner').each(function() {
              if ($(this).height() > height) {
                height = $(this).height();
              }
            });
            if ($('body').hasClass('page-office-ofa') && $branch.hasClass('menu-programs')) {
              height = 0;
            }
            if (height) {
              if (!($.browser.msie && $.browser.version < 8)) {
                $branch.find('.menu-program-inner').css({
                  height: height + 'px'
                });
              }
            }
          }
        },
        closeBranch = function($branch) {
          $branch.removeClass('hover').find('.item-list-wrapper').addClass('element-invisible');
        };

      $links.find('a').focus(function() {
        var $branch = $(this).closest('li.branch');
        openBranch($branch);
      });

      $links.find('a').blur(function() {
        var $branch = $(this).closest('li.branch');
        closeBranch($branch);
      });
      $links.find('li.branch').hover(function() {
        openBranch($(this));
      }, function() {
        closeBranch($(this));
      });
    }
  }

  Drupal.behaviors.acfDefaultInput = {
    attach: function(context, settings) {
      var $forms = $('#search-block-form, #opre-mailing-list-form, #block-acf-research-pages-ocse-find, .block-acf-theme-email-signup form', context);
      if ($forms.length) {
        $forms.each(function() {
          var $form = $(this),
            $input = $form.find('input.form-text'),
            checkInput = function() {
              if ($input.val() === '') {
                $input.addClass('default').val($input.attr('title'));
              }
            };
          $input.focus(function() {
            if ($input.hasClass('default')) {
              $input.removeClass('default').val('');
            }
          });
          $input.blur(function() {
            checkInput();
          });
          $form.submit(function() {
            if ($input.hasClass('default')) {
              return false;
            }
          });
          checkInput();
        })
      }

      var $search = $('#search-block-form');
      if ($search.find('.form-radio').length) {
        var orig_action = $search.attr('action'),
          search_type = 'Site Search';
        $search.find('.form-radio').addClass('element-invisible');
        $search.find('.form-radio:checked').siblings('label').addClass('active');
        $search.find('.form-type-radio').each(function() {
          var $item = $(this),
            height = $item.height(),
            $position = $('<div>').addClass('hint-position'),
            $hint = $('<div>').addClass('hint').text($item.attr('title'));
          if ($item.hasClass('right')) {
            $hint.addClass('bottom-right');
            $position.css({
              right: '100%',
              marginRight: '-44px'
            });
          } else {
            $hint.addClass('bottom-left');
            $position.css('left', -26 + 'px');
          }
          $position.css('top', height + 'px').css('padding-top', '10px');
          $position.append($hint);
          $item.append($position);
          $item.hover(function() {
            $hint.fadeIn(100);
          }, function() {
            $hint.fadeOut(100);
          });
        });

        // chooser for searching google or resource library
        $search.find('input[name=search-mode]').change(function() {
          var mode = $(this).val();
          $search.find('.form-type-radio label').removeClass('active');
          $search.find('.form-radio:checked').siblings('label').addClass('active');
          if (mode == "site") {
            search_type = 'Site Search';
          } else {
            search_type = 'Keyword Search';
          }
          $search.attr("action", dest);
        });

      }
    }
  }

  Drupal.behaviors.acfProgramRail = {
    attach: function(context, settings) {
      var $block = $('#block-acf-theme-programs'),
        $block_content = $block.find('.content'),
        $tabs = $block_content.find('ul.tabs'),
        $items = $tabs.find('li'),
        $desc = $('<ul>').addClass('desc'),
        count = 0,
        width = 180,
        delta,
        max = $items.length,
        pages = Math.ceil(max / 5),
        current = 0,
        position = 0;
      $items.each(function() {
        var text = $(this).find('.inner').html();
        $desc.append($('<li>').html(text));
      });
      $block.find('.content').append($desc);
      var $desc_items = $desc.find('li');
      $items.mouseenter(function() {
        $items.removeClass('hover');
        $desc_items.hide();
        var id = $(this).index();
        $(this).addClass('hover');
        $desc_items.eq(id).show();
      });
      $block_content.mouseleave(function() {
        $items.removeClass('hover');
        $desc_items.hide();
      });
      $items.each(function() {
        delta = count;
        $(this).find('.tab').css({
          left: (width * delta) + 'px'
        });
        count++;
      });
      if (max * width > $tabs.width()) {
        $tabs.css('width', max * width + 'px');
      }
      if (max > 5) {
        var $arrows = $('<ul>').addClass('arrows'),
          gotoPage = function(page) {
            var left = 0 - (page * width * 5);
            $tabs.animate({
              left: left + 'px'
            });
          },
          nextTab = function() {
            current++;
            if (current >= pages) {
              current = 0;
            }
            gotoPage(current);
            /*
            count = 0;
            $items.each(function(){
            delta = count - current;
            if (delta < 0) {
            delta = delta+max;
            }
            $(this).find('.tab').css({left: (width*delta)+'px'});
            count++;
            });
            */
          },
          prevTab = function() {
            current--;
            if (current < 0) {
              current = pages - 1;
            }
            gotoPage(current);
            /*
            count = 0;
            $items.each(function(){
            delta = count - current;
            if (delta < 0) {
            delta = delta+max;
            }
            $(this).find('.tab').css({left: (width*delta)+'px'});
            count++;
            });
            */
          };
        $arrows.append($('<li>').addClass('prev').html($('<a/>').text('Scroll left').attr({
          'href': '#',
          'title': 'Scroll left'
        }).click(function() {
          prevTab();
          return false;
        })));
        $arrows.append($('<li>').addClass('next').html($('<a/>').text('Scroll right').attr({
          'href': '#',
          'title': 'Scroll right'
        }).click(function() {
          nextTab();
          return false;
        })));
        $block.append($arrows);
      }
    }
  }

  Drupal.behaviors.acfSlideshow = {
    attach: function(context, settings) {
      var $block = $('#block-acf-theme-slideshow', context),
        $content = $block.find('.content'),
        $wrapper = $content.find('ul.slides');
      $slides = $wrapper.find('li');

      if ($block.length) {

        if (BrowserDetect.browser == 'Chrome') {
          $('#block-acf-theme-slideshow').find('ul.slides li').css({
            position: 'relative',
            top: 'auto',
            left: 'auto'
          });
        }

        var current = 0,
          height = 310,
          max = $slides.length - 1,
          slide_timeout,
          gotoSlide = function(id) {
            if (id != current) {
              if (Drupal.settings.carousel && Drupal.settings.carousel.video) {
                for (var i = 0; i < Drupal.settings.carousel.video.length; i++) {
                  var video = Drupal.settings.carousel.video[i];
                  if (typeof window['player' + video.nid] == 'object') {
                    try {
                      window['player' + video.nid].pauseVideo();
                    } catch (e) {
                      //console.log('problem with pauseVideo()');
                    }
                  }
                }
              }
              $select.find('li a').removeClass('active');
              $select.find('li.page:eq(' + id + ') a').addClass('active');
              $slides.eq(current).addClass('element-invisible');
              current = id;
              $slides.eq(id).removeClass('element-invisible');
            }
          },
          nextSlide = function() {
            var id = current;
            id++;
            if (id > max) {
              id = 0;
            }
            gotoSlide(id);
          },
          prevSlide = function() {
            var id = current;
            id--;
            if (id < 0) {
              id = max;
            }
            gotoSlide(id);
          },
          $nav = $('<ul>').addClass('nav'),
          $select = $('<ul>').addClass('select');

        oniframeplayerStateChange = function(event) {
          if (event.data == YT.PlayerState.PLAYING) {
            slide_timeout = clearInterval(slide_timeout);
          }
        }

        onytplayerStateChange = function(newState) {
          if (newState !== -1) {
            slide_timeout = clearInterval(slide_timeout);
          }
        }

        if (max > 0) {

          if ($('body').hasClass('page-office-acf-region-office')) {
            $slides.not('.first').addClass('element-invisible');

            $select.append(
              $('<li>').addClass('prev').append(
                $('<a/>').text('Previous slide').attr({
                  href: '#',
                  title: 'Previous'
                }).click(function() {
                  slide_timeout = clearInterval(slide_timeout);
                  prevSlide();
                  return false;
                })
              )
            );

            for (i = current; i <= max; i++) {
              (function(id) {
                var $a = $('<a/>').text('Skip to slide ' + (i + 1)).attr({
                  href: '#' + $slides.eq(id).attr('id')
                }).click(function() {
                  slide_timeout = clearInterval(slide_timeout);
                  gotoSlide(id);
                  return false;
                });
                if (id == 0) {
                  $a.addClass('active');
                }
                $select.append(
                  $('<li>').addClass('page').append($a)
                );
              })(i);
            }

            $select.append(
              $('<li>').addClass('next').append(
                $('<a/>').text('Next slide').attr({
                  href: '#',
                  title: 'Next'
                }).click(function() {
                  slide_timeout = clearInterval(slide_timeout);
                  nextSlide();
                  return false;
                })
              )
            );


            $content.prepend($nav);
            $content.append($('<div>').addClass('select-wrapper').html($select));
            slide_timeout = setInterval(function() {
              nextSlide();
            }, 7250);
          } else {
            for (i = current; i <= max; i++) {
              var $slide = $slides.eq(i),
                $caption = $slide.find('.caption');
              if ($slide.outerHeight() > height) {
                height = $slide.outerHeight();
              }
              if ($caption.height() < 290) {
                var diff = 284 - $slide.find('.caption').height();
                $caption.css('padding-top', (diff / 2));
              }
              if (i != 0) {
                $slide.addClass('element-invisible');
              }
              (function(id) {
                var $a = $('<a/>').attr({
                  href: '#' + $slides.eq(id).attr('id')
                }).click(function() {
                  slide_timeout = clearInterval(slide_timeout);
                  gotoSlide(id);
                  return false;
                }).html($('<span>').text('Skip to slide ' + (i + 1)));
                if (id == 0) {
                  $a.addClass('active');
                }
                $select.append($('<li>').append($a));
              })(i);
            }
            $slides.css('height', height);
            $nav.append($('<li>').addClass('prev').append($('<a/>').text('Previous slide').attr({
              href: '#',
              title: 'Previous'
            }).click(function() {
              slide_timeout = clearInterval(slide_timeout);
              prevSlide();
              return false;
            })));
            $nav.append($('<li>').addClass('next').append($('<a/>').text('Next slide').attr({
              href: '#',
              title: 'Next'
            }).click(function() {
              slide_timeout = clearInterval(slide_timeout);
              nextSlide();
              return false;
            })));
            $content.prepend($nav);
            $content.append($('<div>').addClass('select-wrapper').html($select));
            slide_timeout = setInterval(function() {
              nextSlide();
            }, 7250);
          }
        }
      }

    }
  }




  /**
   * Attaches the Ajax behavior to each Ajax form element.
   */
  Drupal.behaviors.AJAX = {
    attach: function(context, settings) {
      // Load all Ajax behaviors specified in the settings.
      for (var base in settings.ajax) {
        if (!$('#' + base + '.ajax-processed').length) {
          var element_settings = settings.ajax[base];

          if (typeof element_settings.selector == 'undefined') {
            element_settings.selector = '#' + base;
          }
          $(element_settings.selector).each(function() {
            element_settings.element = this;
            Drupal.ajax[base] = new Drupal.ajax(base, this, element_settings);
          });

          $('#' + base).addClass('ajax-processed');
        }
      }

      // Bind Ajax behaviors to all items showing the class.
      $('.use-ajax:not(.ajax-processed)').addClass('ajax-processed').each(function() {
        var element_settings = {};
        // Clicked links look better with the throbber than the progress bar.
        element_settings.progress = {
          'type': 'none'
        };

        // For anchor tags, these will go to the target of the anchor rather
        // than the usual location.
        if ($(this).attr('href')) {
          element_settings.url = $(this).attr('href');
          element_settings.event = 'click';
        }
        var base = $(this).attr('id');
        Drupal.ajax[base] = new Drupal.ajax(base, this, element_settings);
      });

      // This class means to submit the form to the action using Ajax.
      $('.use-ajax-submit:not(.ajax-processed)').addClass('ajax-processed').each(function() {
        var element_settings = {};

        // Ajax submits specified in this manner automatically submit to the
        // normal form action.
        element_settings.url = $(this.form).attr('action');
        // Form submit button clicks need to tell the form what was clicked so
        // it gets passed in the POST request.
        element_settings.setClick = true;
        // Form buttons use the 'click' event rather than mousedown.
        element_settings.event = 'click';
        // Clicked form buttons look better with the throbber than the progress bar.
        element_settings.progress = {
          'type': 'throbber'
        };

        var base = $(this).attr('id');
        Drupal.ajax[base] = new Drupal.ajax(base, this, element_settings);
      });
    }
  };

  Drupal.behaviors.fixFileLinks = {
    attach: function(context, settings) {
      var $block = $('#block-acf-theme-ohs-pre-app-resources');
      if ($block.length) {
        $block.find('a.pdf, a.zip').each(function() {
          $(this).prepend($('<span/>').addClass('icon'));
        });
      }
    }
  };

  Drupal.behaviors.moreLess = {
    attach: function(context, settings) {
      $('.more-less', context).each(function() {
        var $block = $(this),
          $more = $block.find('.more-text'),
          toggle_more = function() {
            if ($more.hasClass('element-invisible')) {
              $more.removeClass('element-invisible');
              $hide.removeClass('element-invisible');
              $link.text('Hide');
            } else {
              $hide.addClass('element-invisible');
              $more.addClass('element-invisible');
              $link.text('Show More');

            }
          },
          $hide = $('<a/>').text('Hide').addClass('show-more more element-invisible').attr({
            'href': '#'
          }).click(function(e) {
            e.preventDefault();
            toggle_more();
          }),
          $link = $('<a/>').text('Show More').addClass('show-more more').attr({
            'href': '#'
          }).click(function(e) {
            e.preventDefault();
            toggle_more();
          });
        $more.before($hide);
        $more.after($link);
      });
    }
  };

  Drupal.behaviors.imageCaptions = {
    attach: function(context, settings) {
      var sizeCaptions = function() {
        $('.asset-image-wrapper').each(function() {
          var $wrapper = $(this),
            $img = $wrapper.find('img'),
            width = $img.attr('width');
          if (width > 0 && !$wrapper.hasClass('form')) {
            $img.css('width', '100%');
            $wrapper.css({
              'max-width': width + 'px',
              width: '100%'
            });
          }
        });
      };
      sizeCaptions();
      $(window).smartresize(function() {
        sizeCaptions();
      });
    }
  };

  Drupal.behaviors.acfReports = {
    attach: function(context, settings) {
      $('.node-acf-report.full').find('.summary').each(function() {
        var $jar = $(this),
          $summary = $jar.find('.report-body'),
          $questions = $jar.find('.report-questions');
        $summary.find('.content').prepend($questions.clone());
      });
      $('.node-acf-report.full').find('.report-body').each(function() {
        var $jar = $(this),
          $content = $jar.find('.content'),
          $toggle_wrapper = $('<div>').addClass('expand-wrapper'),
          $toggle = $('<a/>').attr('href', '#').addClass('expand collapsed').click(function(e) {
            e.preventDefault();
            if ($(this).hasClass('collapsed')) {
              $(this).removeClass('collapsed').addClass('expanded');
              $content.removeClass('element-invisible');
            } else {
              $(this).addClass('collapsed').removeClass('expanded');
              $content.addClass('element-invisible');
            }
          });
        if (!$jar.hasClass('no-expand-collapse')) {
          $toggle_wrapper.append($toggle);
          $jar.append($toggle_wrapper);
        }
        $content.addClass('element-invisible');
        // expand summary
        if ($(this).parent().hasClass('summary')) {
          $toggle.removeClass('collapsed').addClass('expanded');
          $content.removeClass('element-invisible');
        }
      });
    }
  }

}(jQuery));
;
