!function (f) {
  if ('object' == typeof exports && 'undefined' != typeof module) module.exports = f();
   else if ('function' == typeof define && define.amd) define([], f);
   else {
    var g;
    g = 'undefined' != typeof window ? window : 'undefined' != typeof global ? global : 'undefined' != typeof self ? self : this,
    g.nativeEmoji = f()
  }
}(
  function () {
    var define;
    return function () {
      function r(e, n, t) {
        function o(i, f) {
          if (!n[i]) {
            if (!e[i]) {
              var c = 'function' == typeof require &&
              require;
              if (!f && c) return c(i, !0);
              if (u) return u(i, !0);
              var a = new Error('Cannot find module \'' + i + '\'');
              throw a.code = 'MODULE_NOT_FOUND',
              a
            }
            var p = n[i] = {
              exports: {
              }
            };
            e[i][0].call(
              p.exports,
              function (r) {
                return o(e[i][1][r] || r)
              },
              p,
              p.exports,
              r,
              e,
              n,
              t
            )
          }
          return n[i].exports
        }
        for (var u = 'function' == typeof require && require, i = 0; i < t.length; i++) o(t[i]);
        return o
      }
      return r
    }() ({
      1: [
        function (require, module, exports) {
          'use strict';
          !function (global, factory) {
            if ('function' == typeof define && define.amd) define(['module'], factory);
             else if (void 0 !== exports) factory(module);
             else {
              var mod = {
                exports: {
                }
              };
              factory(mod),
              global.undefined = mod.exports
            }
          }(
            void 0,
            function (module) {
              function _typeof(obj) {
                '@babel/helpers - typeof';
                return (
                  _typeof = 'function' == typeof Symbol &&
                  'symbol' == typeof Symbol.iterator ? function (obj) {
                    return typeof obj
                  }
                   : function (obj) {
                    return obj &&
                    'function' == typeof Symbol &&
                    obj.constructor === Symbol &&
                    obj !== Symbol.prototype ? 'symbol' : typeof obj
                  }
                ) (obj)
              }
              function _classCallCheck(instance, Constructor) {
                if (!(instance instanceof Constructor)) throw new TypeError('Cannot call a class as a function')
              }
              function _defineProperties(target, props) {
                for (var i = 0; i < props.length; i++) {
                  var descriptor = props[i];
                  descriptor.enumerable = descriptor.enumerable ||
                  !1,
                  descriptor.configurable = !0,
                  'value' in descriptor &&
                  (descriptor.writable = !0),
                  Object.defineProperty(target, _toPropertyKey(descriptor.key), descriptor)
                }
              }
              function _createClass(Constructor, protoProps, staticProps) {
                return protoProps &&
                _defineProperties(Constructor.prototype, protoProps),
                staticProps &&
                _defineProperties(Constructor, staticProps),
                Object.defineProperty(Constructor, 'prototype', {
                  writable: !1
                }),
                Constructor
              }
              function _toPropertyKey(arg) {
                var key = _toPrimitive(arg, 'string');
                return 'symbol' == typeof key ? key : String(key)
              }
              function _toPrimitive(input, hint) {
                if ('object' !== _typeof(input) || null === input) return input;
                var prim = input[Symbol.toPrimitive];
                if (void 0 !== prim) {
                  var res = prim.call(input, hint || 'default');
                  if ('object' !== _typeof(res)) return res;
                  throw new TypeError('@@toPrimitive must return a primitive value.')
                }
                return ('string' === hint ? String : Number) (input)
              }
              var nativeEmoji = function () {
                function nativeEmoji() {
                  _classCallCheck(this, nativeEmoji),
                  this.initiate()
                }
                return _createClass(
                  nativeEmoji,
                  [
                    {
                      key: 'initiate',
                      value: function () {
                        var _this = this;
                        document.querySelectorAll(
                          '[data-native-emoji="true"], [data-native-emoji-large="true"]'
                        ).forEach(function (element) {
                          _this.generateElements(element)
                        })
                      }
                    },
                    {
                      key: 'generateElements',
                      value: function (emojiInput) {
                        var clickLink = function (event) {
                          var caretPos = emojiInput.selectionStart;
                          emojiInput.value = event.target.innerHTML,
                          emojiContainer.classList.add('emoji-picker-open'),
                          'undefined' != typeof angular &&
                          angular.element(emojiInput).triggerHandler('change')
                        },
                        clickCategory = function (event) {
                          emojiInput.selectionStart;
                          emojiContainer.classList.add('emoji-picker-open');
                          var hideUls = emojiPicker.querySelectorAll('ul'),
                          i = 1,
                          l = hideUls.length;
                          for (i; i < l; i++) hideUls[i].style.display = 'none';
                          var backgroundToggle = emojiPicker.querySelectorAll('.emoji-picker-tabs a');
                          for (i = 0, l = backgroundToggle.length, i; i < l; i++) backgroundToggle[i].classList.remove('active');
                          
                          // Get the category ID from the clicked element or its parent anchor
                          var categoryId = event.target.id || (event.target.closest('a') && event.target.closest('a').id);
                          
                          if (categoryId) {
                            var targetList = emojiPicker.querySelector('.emoji-picker-list-' + categoryId);
                            var targetTab = emojiPicker.querySelector('#' + categoryId);
                            
                            if (targetList) {
                              targetList.style.display = 'block';
                            }
                            if (targetTab) {
                              targetTab.classList.add('active');
                            }
                          }
                        };
                        emojiInput.style.width = '100%';
                        var emojiContainer = document.createElement('div');
                        emojiContainer.classList.add('emoji-picker-container'),
                        emojiInput.parentNode.replaceChild(emojiContainer, emojiInput),
                        emojiContainer.appendChild(emojiInput);
                        var emojiPicker = document.createElement('div');
                        emojiPicker.tabIndex = 0,
                        emojiPicker.classList.add('emoji-picker'),
                        emojiInput.hasAttribute('data-native-emoji-large');
                        var emojiTrigger = document.createElement('button');
                        emojiTrigger.classList.add('emoji-picker-trigger'),
                        emojiTrigger.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 12 14"><path d="M8.9 8.4q-0.3 0.9-1.1 1.5t-1.8 0.6-1.8-0.6-1.1-1.5q-0.1-0.2 0-0.4t0.3-0.2q0.2-0.1 0.4 0t0.2 0.3q0.2 0.6 0.7 1t1.2 0.4 1.2-0.4 0.7-1q0.1-0.2 0.3-0.3t0.4 0 0.3 0.2 0 0.4zM5 5q0 0.4-0.3 0.7t-0.7 0.3-0.7-0.3-0.3-0.7 0.3-0.7 0.7-0.3 0.7 0.3 0.3 0.7zM9 5q0 0.4-0.3 0.7t-0.7 0.3-0.7-0.3-0.3-0.7 0.3-0.7 0.7-0.3 0.7 0.3 0.3 0.7zM11 7q0-1-0.4-1.9t-1.1-1.6-1.6-1.1-1.9-0.4-1.9 0.4-1.6 1.1-1.1 1.6-0.4 1.9 0.4 1.9 1.1 1.6 1.6 1.1 1.9 0.4 1.9-0.4 1.6-1.1 1.1-1.6 0.4-1.9zM12 7q0 1.6-0.8 3t-2.2 2.2-3 0.8-3-0.8-2.2-2.2-0.8-3 0.8-3 2.2-2.2 3-0.8 3 0.8 2.2 2.2 0.8 3z"/></svg>',
                        emojiTrigger.onclick = function (e) {
                          e.preventDefault();
                          emojiContainer.classList.toggle('emoji-picker-open'),
                          emojiPicker.focus()
                        },
                        emojiInput.hasAttribute('data-native-emoji-large') ||
                        emojiContainer.appendChild(emojiTrigger),
                        window.addEventListener(
                          'click',
                          function (e) {
                            emojiInput.hasAttribute('data-native-emoji-large') ||
                            emojiContainer.classList.contains('emoji-picker-open') &&
                            (
                              emojiPicker.contains(e.target) ||
                              emojiTrigger.contains(e.target) ||
                              emojiContainer.classList.remove('emoji-picker-open')
                            )
                          }
                        );
                        var facesCategory = document.createElement('ul');
                        facesCategory.classList.add('emoji-picker-list', 'emoji-picker-list-faces');
                        var animalsCategory = document.createElement('ul');
                        animalsCategory.classList.add('emoji-picker-list', 'emoji-picker-list-animals'),
                        animalsCategory.style.display = 'none';
                        var foodCategory = document.createElement('ul');
                        foodCategory.classList.add('emoji-picker-list', 'emoji-picker-list-food'),
                        foodCategory.style.display = 'none';
                        var sportCategory = document.createElement('ul');
                        sportCategory.classList.add('emoji-picker-list', 'emoji-picker-list-sport'),
                        sportCategory.style.display = 'none';
                        var transportCategory = document.createElement('ul');
                        transportCategory.classList.add('emoji-picker-list', 'emoji-picker-list-transport'),
                        transportCategory.style.display = 'none';
                        var objectsCategory = document.createElement('ul');
                        objectsCategory.classList.add('emoji-picker-list', 'emoji-picker-list-objects'),
                        objectsCategory.style.display = 'none';
                        var flagsCategory = document.createElement('ul');
                        flagsCategory.classList.add('emoji-picker-list', 'emoji-picker-list-flags'),
                        flagsCategory.style.display = 'none';
                        var emojiCategory = document.createElement('ul');
                        emojiCategory.classList.add('emoji-picker-tabs');
                        var emojiCategories = new Array;
                        emojiCategories.push({
                          name: 'faces',
                          svg: '<svg id="faces" data-name="Layer 1" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 150 150"><path id="faces" d="M74.34,128.48a53.5,53.5,0,1,1,37.84-15.67,53.16,53.16,0,0,1-37.84,15.67Zm0-97.89a44.4,44.4,0,1,0,31.4,13,44.07,44.07,0,0,0-31.4-13Z"/><path id="faces" d="M74.35,108A33.07,33.07,0,0,1,41.29,75a2.28,2.28,0,0,1,2.27-2.28h0A2.27,2.27,0,0,1,45.83,75a28.52,28.52,0,0,0,57,0,2.27,2.27,0,0,1,4.54,0A33.09,33.09,0,0,1,74.35,108Z"/><path id="faces" d="M58.84,62a6.81,6.81,0,1,0,6.81,6.81A6.81,6.81,0,0,0,58.84,62Z"/><path id="faces" d="M89.87,62a6.81,6.81,0,1,0,6.81,6.81A6.82,6.82,0,0,0,89.87,62Z"/></svg>'
                        }),
                        emojiCategories.push({
                          name: 'animals',
                          svg: '<svg id="animals" data-name="Layer 1" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 150 150"><path id="animals" d="M59.9,91.75h0c-22.46,0-41.82-19.34-44.09-44A52.1,52.1,0,0,1,16,36.8a4.51,4.51,0,0,1,2.63-3.62,39.79,39.79,0,0,1,12.74-3.37c23.92-2.15,45.35,17.83,47.74,43.86a52.77,52.77,0,0,1-.15,10.93,4.56,4.56,0,0,1-2.64,3.62,39.67,39.67,0,0,1-12.73,3.36c-1.23.11-2.45.17-3.66.17ZM24.76,40.49a41.29,41.29,0,0,0,.09,6.4C26.7,67,42.09,82.66,59.9,82.67h0c.94,0,1.88,0,2.83-.14a30.39,30.39,0,0,0,7.41-1.62,41.14,41.14,0,0,0-.11-6.4C68.09,53.38,51.11,37.08,32.17,38.86a30.78,30.78,0,0,0-7.41,1.63Z"/><path id="animals" d="M36.68,125.64a4.53,4.53,0,0,1-4.33-3.17,53.32,53.32,0,0,1-2.26-11A50.42,50.42,0,0,1,39.51,76.6c7.35-9.91,17.84-16,29.5-17,1.16-.11,2.33-.13,3.47-.13a4.54,4.54,0,0,1,4.33,3.16,51.59,51.59,0,0,1,2.27,11.08,50.39,50.39,0,0,1-9.42,34.8c-7.35,9.91-17.83,16-29.5,17a17.63,17.63,0,0,1-3.48.12ZM69.09,68.69A32.41,32.41,0,0,0,46.8,82a42.57,42.57,0,0,0-6.71,34.38,32.38,32.38,0,0,0,22.28-13.32A41.35,41.35,0,0,0,70,74.51a39.38,39.38,0,0,0-.94-5.82Z"/><path id="animals" d="M90.27,91.75c-1.22,0-2.43-.06-3.66-.17a39.67,39.67,0,0,1-12.73-3.36,4.57,4.57,0,0,1-2.64-3.61,53.38,53.38,0,0,1-.17-10.93c2.41-26,23.7-46.07,47.76-43.87a39.74,39.74,0,0,1,12.73,3.37,4.57,4.57,0,0,1,2.64,3.62,53.35,53.35,0,0,1,.16,10.92c-2.28,24.69-21.65,44-44.09,44ZM80,80.91a30.57,30.57,0,0,0,7.42,1.62c19.07,1.78,35.92-14.53,37.87-35.64a42.55,42.55,0,0,0,.1-6.4A30.86,30.86,0,0,0,118,38.86C99,37.07,82.06,53.38,80.12,74.51a43.91,43.91,0,0,0-.1,6.4Z"/><path id="animals" d="M113.49,125.64h0c-1.16,0-2.3,0-3.46-.12-23.9-2.21-41.36-25.47-38.94-51.85A53.52,53.52,0,0,1,73.34,62.6a4.55,4.55,0,0,1,4.33-3.16c1.16,0,2.34,0,3.51.13,11.64,1.07,22.11,7.12,29.48,17a50.51,50.51,0,0,1,9.42,34.81,53.51,53.51,0,0,1-2.26,11,4.54,4.54,0,0,1-4.33,3.19ZM81.08,68.69a42.53,42.53,0,0,0-1,5.82c-1.94,21.1,11.45,39.71,29.95,41.88A42.38,42.38,0,0,0,103.36,82,32.42,32.42,0,0,0,81.08,68.69Z"/><path id="animals" d="M75.08,45.45a7.83,7.83,0,1,0,7.83,7.83,7.83,7.83,0,0,0-7.83-7.83Z"/><path id="animals" d="M76.29,51.89a2.26,2.26,0,0,1-2.14-3A46,46,0,0,1,92.82,25.34a2.27,2.27,0,1,1,2.4,3.86A41.4,41.4,0,0,0,78.43,50.39a2.28,2.28,0,0,1-2.14,1.5Z"/><path id="animals" d="M73.87,51.89a2.28,2.28,0,0,1-2.14-1.5A41.35,41.35,0,0,0,54.94,29.2a2.27,2.27,0,0,1,2.39-3.86A46,46,0,0,1,76,48.85a2.28,2.28,0,0,1-1.37,2.91,2.31,2.31,0,0,1-.77.13Z"/></svg>'
                        }),
                        emojiCategories.push({
                          name: 'food',
                          svg: '<svg id="food" data-name="Layer 1" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 150 150"><path id="food" d="M104,20.76h.15c15.83.52,24.08,21.48,24.07,32.56.26,12.42-10.72,23.55-24,24.21a3.53,3.53,0,0,1-.46,0c-13.25-.66-24.23-11.8-24-24.3,0-11,8.26-31.95,24.07-32.47Zm0,47.69c8.25-.54,15.3-7.51,15.14-15,0-8.12-6.22-23.1-15.14-23.57-8.9.46-15.14,15.45-15.14,23.48-.14,7.61,6.9,14.59,15.14,15.13Z"/><path id="food" d="M97.19,69.21h.14a4.53,4.53,0,0,1,4.4,4.68l-1.48,46.92a1.59,1.59,0,0,0,.5,1.06,4.6,4.6,0,0,0,3.25,1.19h0a4.57,4.57,0,0,0,3.26-1.2,1.53,1.53,0,0,0,.49-1l-1.48-46.95a4.54,4.54,0,1,1,9.08-.28l1.47,46.91a10.42,10.42,0,0,1-3,7.65,13.65,13.65,0,0,1-9.81,4h0a13.58,13.58,0,0,1-9.79-4,10.42,10.42,0,0,1-3-7.67l1.48-46.89a4.53,4.53,0,0,1,4.53-4.4Z"/><path id="food" d="M41.84,69.21H42a4.53,4.53,0,0,1,4.4,4.68L44.9,120.81a1.57,1.57,0,0,0,.5,1.06,4.6,4.6,0,0,0,3.25,1.19h0a4.51,4.51,0,0,0,3.24-1.19,1.48,1.48,0,0,0,.5-1L50.93,73.89a4.53,4.53,0,0,1,4.39-4.68A4.4,4.4,0,0,1,60,73.61l1.48,46.91a10.49,10.49,0,0,1-3,7.66,13.57,13.57,0,0,1-9.78,4h0a13.59,13.59,0,0,1-9.78-4,10.48,10.48,0,0,1-3-7.67l1.48-46.9a4.54,4.54,0,0,1,4.54-4.4Z"/><path id="food" d="M28.59,20.76a4.54,4.54,0,0,1,4.54,4.54V51a15.52,15.52,0,0,0,31,0V25.3a4.55,4.55,0,0,1,9.09,0V51a24.61,24.61,0,1,1-49.21,0V25.3a4.54,4.54,0,0,1,4.54-4.54Z"/><path id="food" d="M55.34,20.76a4.54,4.54,0,0,1,4.54,4.54v19a4.54,4.54,0,1,1-9.08,0v-19a4.54,4.54,0,0,1,4.54-4.54Z"/><path id="food" d="M42,20.76a4.54,4.54,0,0,1,4.54,4.54v19a4.54,4.54,0,1,1-9.08,0v-19A4.54,4.54,0,0,1,42,20.76Z"/></svg>'
                        }),
                        emojiCategories.push({
                          name: 'sport',
                          svg: '<svg id="sport" data-name="Layer 1" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 150 150"><path id="sport" d="M75.35,130.24a53.49,53.49,0,1,1,53.48-53.49,53.55,53.55,0,0,1-53.48,53.49Zm0-97.89a44.41,44.41,0,1,0,44.4,44.4,44.1,44.1,0,0,0-44.4-44.4Z"/><path id="sport" d="M119.24,84.08A51.29,51.29,0,0,1,68,32.86a49.44,49.44,0,0,1,.26-5,2.26,2.26,0,0,1,2-2c1.66-.16,3.34-.25,5-.25a51.26,51.26,0,0,1,51.21,51.21c0,1.71-.09,3.38-.25,5a2.28,2.28,0,0,1-2,2c-1.65.16-3.33.25-5,.25ZM72.64,30.16c-.06.9-.08,1.79-.08,2.7a46.73,46.73,0,0,0,46.68,46.68q1.37,0,2.7-.09c.06-.89.08-1.79.08-2.7A46.72,46.72,0,0,0,75.35,30.08c-.91,0-1.82,0-2.71.08Z"/><path id="sport" d="M75.35,128A51.28,51.28,0,0,1,24.12,76.76c0-1.7.1-3.38.25-5a2.29,2.29,0,0,1,2-2c1.66-.16,3.33-.25,5.05-.25a51.27,51.27,0,0,1,51.21,51.22c0,1.69-.09,3.37-.25,5a2.27,2.27,0,0,1-2,2c-1.66.16-3.32.25-5,.25ZM28.75,74.05c-.05.9-.09,1.8-.09,2.71a46.74,46.74,0,0,0,46.69,46.67c.91,0,1.8,0,2.7-.08,0-.9.08-1.8.08-2.7A46.73,46.73,0,0,0,31.46,74c-.91,0-1.81,0-2.71.08Z"/><polygon id="sport" points="42.69 112.61 39.48 109.4 108 40.88 111.21 44.1 42.69 112.61 42.69 112.61"/></svg>'
                        }),
                        emojiCategories.push({
                          name: 'transport',
                          svg: '<svg id="transport" data-name="Layer 1" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 150 150"><path id="transport" d="M120.7,116H31a4.55,4.55,0,0,1-4.54-4.55V54.28A31.82,31.82,0,0,1,58.25,22.49h35.2a31.83,31.83,0,0,1,31.8,31.79v57.15A4.55,4.55,0,0,1,120.7,116Zm-85.16-9.09h80.62V54.28A22.74,22.74,0,0,0,93.45,31.57H58.25A22.74,22.74,0,0,0,35.54,54.28v52.61Z"/><path id="transport" d="M49.35,129.23c-8.53,0-13.62-2.77-13.62-7.41V115.6a4.54,4.54,0,1,1,9.08,0v4.06a21.32,21.32,0,0,0,9.09,0V115.6a4.54,4.54,0,0,1,9.08,0v6.22c0,4.64-5.09,7.41-13.63,7.41Z"/><path id="transport" d="M102.34,129.23c-8.53,0-13.62-2.77-13.62-7.41V115.6a4.54,4.54,0,0,1,9.08,0v4.06a21.28,21.28,0,0,0,9.08,0V115.6a4.55,4.55,0,0,1,9.09,0v6.22c0,4.64-5.09,7.41-13.63,7.41Z"/><path id="transport" d="M97.81,44.83H53.9a4.55,4.55,0,1,1,0-9.09H97.81a4.55,4.55,0,0,1,0,9.09Z"/><path id="transport" d="M54.28,84.2A6.8,6.8,0,1,0,61.07,91a6.8,6.8,0,0,0-6.79-6.8Z"/><path id="transport" d="M97.43,84.2a6.8,6.8,0,1,0,6.79,6.8,6.8,6.8,0,0,0-6.79-6.8Z"/><path id="transport" d="M107.08,81H44.63a6.82,6.82,0,0,1-6.82-6.82V54.28a6.82,6.82,0,0,1,6.82-6.81h62.45a6.82,6.82,0,0,1,6.81,6.81V74.15A6.83,6.83,0,0,1,107.08,81ZM44.63,52a2.28,2.28,0,0,0-2.28,2.27V74.15a2.28,2.28,0,0,0,2.28,2.27h62.45a2.27,2.27,0,0,0,2.27-2.27V54.28A2.27,2.27,0,0,0,107.08,52Z"/></svg>'
                        }),
                        emojiCategories.push({
                          name: 'objects',
                          svg: '<svg id="objects" data-name="Layer 1" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 150 150"><path id="objects" d="M107.78,129a4.55,4.55,0,0,1-2.67-.87l-30-21.79-30,21.79a4.53,4.53,0,0,1-5.34,0,4.58,4.58,0,0,1-1.65-5.08L49.59,87.82,19.6,66a4.54,4.54,0,0,1,2.67-8.22H59.34L70.8,22.55a4.55,4.55,0,0,1,8.64,0L90.89,57.81H128A4.54,4.54,0,0,1,130.63,66l-30,21.79,11.46,35.25a4.55,4.55,0,0,1-4.32,6ZM75.12,96.2a4.53,4.53,0,0,1,2.67.87l21.35,15.51L91,87.49a4.55,4.55,0,0,1,1.65-5.08L114,66.89H87.59a4.54,4.54,0,0,1-4.32-3.13l-8.15-25.1L67,63.76a4.53,4.53,0,0,1-4.32,3.13H36.25L57.61,82.41a4.54,4.54,0,0,1,1.65,5.08l-8.17,25.09L72.45,97.07a4.53,4.53,0,0,1,2.67-.87Z"/></svg>'
                        });
                        emojiCategories.push({
                          name: 'flags',
                          svg: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M5 22V14M5 14L7.47067 13.5059C9.1212 13.1758 10.8321 13.3328 12.3949 13.958C14.0885 14.6354 15.9524 14.7619 17.722 14.3195L17.8221 14.2945C18.4082 14.148 18.6861 13.4769 18.3753 12.9589L16.8147 10.3578C16.4732 9.78863 16.3024 9.50405 16.2619 9.19451C16.2451 9.06539 16.2451 8.93461 16.2619 8.80549C16.3024 8.49595 16.4732 8.21137 16.8147 7.64221L18.0932 5.51132C18.4278 4.9536 17.9211 4.26972 17.2901 4.42746C15.8013 4.79967 14.2331 4.69323 12.8082 4.12329L12.3949 3.95797C10.8321 3.33284 9.1212 3.17576 7.47067 3.50587L5 4M5 14V11M5 4V2M5 4V7" stroke="#1C274C" stroke-width="1.5" stroke-linecap="round"/></svg>'
                        });
var faces = [];
var animals = [];
var food = [];
var sport = [];
var transport = [];
var objects = [];
var flags = [];

fetch("/static/emoji.json")
.then(res => res.json())
.then(data => {
    data.forEach(group => {
    const emojis = group.emojis.map(e => e.emoji);
    switch (group.name) {
        case 'faces':
          faces.push(...emojis);
          break;
        case 'animals':
          animals.push(...emojis);
          break;
        case 'food':
          food.push(...emojis);
          break;
        case 'sport':
          sport.push(...emojis);
          break;
        case 'transport':
          transport.push(...emojis);
          break;
        case 'objects':
          objects.push(...emojis);
          break;
        case 'flags':
          flags.push(...emojis);
          break;
    }});
    
    // Render emojis after loading
    renderAllEmojis();
})
.catch(error => {
    console.error('Failed to load emojis:', error);
});

                        var renderEmoji = function (item, category) {
                          var emojiLi = document.createElement('li'),
                          emojiLink = document.createElement('button');
                          emojiLink.classList.add('emoji-picker-emoji'),
                          emojiLink.innerHTML = item,
                          emojiLink.onmousedown = clickLink,
                          emojiLink.onclick = function (e) {
                            e.preventDefault();
                          },
                          emojiLi.appendChild(emojiLink),
                          category.appendChild(emojiLi)
                        };
                        
                        var renderAllEmojis = function() {
                          // Clear existing emojis first
                          facesCategory.innerHTML = '';
                          animalsCategory.innerHTML = '';
                          foodCategory.innerHTML = '';
                          sportCategory.innerHTML = '';
                          transportCategory.innerHTML = '';
                          objectsCategory.innerHTML = '';
                          flagsCategory.innerHTML = '';
                          
                          // Render emojis
                          faces.map(function (item) {
                            renderEmoji(item, facesCategory)
                          });
                          animals.map(function (item) {
                            renderEmoji(item, animalsCategory)
                          });
                          food.map(function (item) {
                            renderEmoji(item, foodCategory)
                          });
                          sport.map(function (item) {
                            renderEmoji(item, sportCategory)
                          });
                          transport.map(function (item) {
                            renderEmoji(item, transportCategory)
                          });
                          objects.map(function (item) {
                            renderEmoji(item, objectsCategory)
                          });
                          flags.map(function (item) {
                            renderEmoji(item, flagsCategory)
                          });
                        };
                        
                        emojiCategories.map(
                          function (item) {
                            var emojiLi = document.createElement('li'),
                            emojiAnchor = document.createElement('a');
                            emojiAnchor.setAttribute('href', 'javascript:void(0)'),
                            emojiAnchor.id = String(item.name),
                            emojiAnchor.classList.add('emoji-picker-anchor'),
                            'faces' == String(item.name) &&
                            emojiAnchor.classList.add('active'),
                            emojiAnchor.innerHTML = String(item.svg),
                            emojiAnchor.onmousedown = clickCategory,
                            emojiLi.appendChild(emojiAnchor),
                            emojiCategory.appendChild(emojiLi)
                          }
                        );
                        emojiPicker.appendChild(emojiCategory);
                        emojiPicker.appendChild(facesCategory);
                        emojiPicker.appendChild(animalsCategory);
                        emojiPicker.appendChild(foodCategory);
                        emojiPicker.appendChild(sportCategory);
                        emojiPicker.appendChild(transportCategory);
                        emojiPicker.appendChild(objectsCategory);
                        emojiPicker.appendChild(flagsCategory);
                        emojiContainer.appendChild(emojiPicker);
                      }
                    }
                  ]
                ),
                nativeEmoji
              }();
              module.exports = nativeEmoji
            }
          )
        },
        {
        }
      ]
    }, {
    }, [
      1
    ]) (1)
  }
);

