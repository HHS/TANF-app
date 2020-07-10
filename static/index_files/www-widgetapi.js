(function(){/*

 Copyright The Closure Library Authors.
 SPDX-License-Identifier: Apache-2.0
*/
var q;function aa(a){var b=0;return function(){return b<a.length?{done:!1,value:a[b++]}:{done:!0}}}
var ba="function"==typeof Object.defineProperties?Object.defineProperty:function(a,b,c){if(a==Array.prototype||a==Object.prototype)return a;a[b]=c.value;return a};
function ca(a){a=["object"==typeof globalThis&&globalThis,a,"object"==typeof window&&window,"object"==typeof self&&self,"object"==typeof global&&global];for(var b=0;b<a.length;++b){var c=a[b];if(c&&c.Math==Math)return c}throw Error("Cannot find global object");}
var da=ca(this);function t(a,b){if(b)a:{for(var c=da,d=a.split("."),e=0;e<d.length-1;e++){var f=d[e];if(!(f in c))break a;c=c[f]}d=d[d.length-1];e=c[d];f=b(e);f!=e&&null!=f&&ba(c,d,{configurable:!0,writable:!0,value:f})}}
t("Symbol",function(a){function b(e){if(this instanceof b)throw new TypeError("Symbol is not a constructor");return new c("jscomp_symbol_"+(e||"")+"_"+d++,e)}
function c(e,f){this.f=e;ba(this,"description",{configurable:!0,writable:!0,value:f})}
if(a)return a;c.prototype.toString=function(){return this.f};
var d=0;return b});
t("Symbol.iterator",function(a){if(a)return a;a=Symbol("Symbol.iterator");for(var b="Array Int8Array Uint8Array Uint8ClampedArray Int16Array Uint16Array Int32Array Uint32Array Float32Array Float64Array".split(" "),c=0;c<b.length;c++){var d=da[b[c]];"function"===typeof d&&"function"!=typeof d.prototype[a]&&ba(d.prototype,a,{configurable:!0,writable:!0,value:function(){return ea(aa(this))}})}return a});
function ea(a){a={next:a};a[Symbol.iterator]=function(){return this};
return a}
function u(a){var b="undefined"!=typeof Symbol&&Symbol.iterator&&a[Symbol.iterator];return b?b.call(a):{next:aa(a)}}
function fa(a){for(var b,c=[];!(b=a.next()).done;)c.push(b.value);return c}
var ha="function"==typeof Object.create?Object.create:function(a){function b(){}
b.prototype=a;return new b},ia;
if("function"==typeof Object.setPrototypeOf)ia=Object.setPrototypeOf;else{var ja;a:{var ka={a:!0},la={};try{la.__proto__=ka;ja=la.a;break a}catch(a){}ja=!1}ia=ja?function(a,b){a.__proto__=b;if(a.__proto__!==b)throw new TypeError(a+" is not extensible");return a}:null}var ma=ia;
function w(a,b){a.prototype=ha(b.prototype);a.prototype.constructor=a;if(ma)ma(a,b);else for(var c in b)if("prototype"!=c)if(Object.defineProperties){var d=Object.getOwnPropertyDescriptor(b,c);d&&Object.defineProperty(a,c,d)}else a[c]=b[c];a.F=b.prototype}
function na(){this.m=!1;this.i=null;this.g=void 0;this.f=1;this.j=this.l=0;this.B=this.h=null}
function pa(a){if(a.m)throw new TypeError("Generator is already running");a.m=!0}
na.prototype.s=function(a){this.g=a};
function qa(a,b){a.h={ha:b,V:!0};a.f=a.l||a.j}
na.prototype["return"]=function(a){this.h={"return":a};this.f=this.j};
function x(a,b,c){a.f=c;return{value:b}}
na.prototype.v=function(a){this.f=a};
function ra(a){a.l=2;a.j=3}
function sa(a){a.l=0;a.h=null}
function ta(a){a.B=[a.h];a.l=0;a.j=0}
function ua(a){var b=a.B.splice(0)[0];(b=a.h=a.h||b)?b.V?a.f=a.l||a.j:void 0!=b.v&&a.j<b.v?(a.f=b.v,a.h=null):a.f=a.j:a.f=0}
function va(a){this.f=new na;this.g=a}
function wa(a,b){pa(a.f);var c=a.f.i;if(c)return xa(a,"return"in c?c["return"]:function(d){return{value:d,done:!0}},b,a.f["return"]);
a.f["return"](b);return ya(a)}
function xa(a,b,c,d){try{var e=b.call(a.f.i,c);if(!(e instanceof Object))throw new TypeError("Iterator result "+e+" is not an object");if(!e.done)return a.f.m=!1,e;var f=e.value}catch(g){return a.f.i=null,qa(a.f,g),ya(a)}a.f.i=null;d.call(a.f,f);return ya(a)}
function ya(a){for(;a.f.f;)try{var b=a.g(a.f);if(b)return a.f.m=!1,{value:b.value,done:!1}}catch(c){a.f.g=void 0,qa(a.f,c)}a.f.m=!1;if(a.f.h){b=a.f.h;a.f.h=null;if(b.V)throw b.ha;return{value:b["return"],done:!0}}return{value:void 0,done:!0}}
function za(a){this.next=function(b){pa(a.f);a.f.i?b=xa(a,a.f.i.next,b,a.f.s):(a.f.s(b),b=ya(a));return b};
this["throw"]=function(b){pa(a.f);a.f.i?b=xa(a,a.f.i["throw"],b,a.f.s):(qa(a.f,b),b=ya(a));return b};
this["return"]=function(b){return wa(a,b)};
this[Symbol.iterator]=function(){return this}}
function z(a,b){var c=new za(new va(b));ma&&a.prototype&&ma(c,a.prototype);return c}
t("Reflect.setPrototypeOf",function(a){return a?a:ma?function(b,c){try{return ma(b,c),!0}catch(d){return!1}}:null});
function Aa(a,b,c){if(null==a)throw new TypeError("The 'this' value for String.prototype."+c+" must not be null or undefined");if(b instanceof RegExp)throw new TypeError("First argument to String.prototype."+c+" must not be a regular expression");return a+""}
t("String.prototype.endsWith",function(a){return a?a:function(b,c){var d=Aa(this,b,"endsWith");b+="";void 0===c&&(c=d.length);for(var e=Math.max(0,Math.min(c|0,d.length)),f=b.length;0<f&&0<e;)if(d[--e]!=b[--f])return!1;return 0>=f}});
t("String.prototype.startsWith",function(a){return a?a:function(b,c){var d=Aa(this,b,"startsWith");b+="";for(var e=d.length,f=b.length,g=Math.max(0,Math.min(c|0,d.length)),k=0;k<f&&g<e;)if(d[g++]!=b[k++])return!1;return k>=f}});
function Ba(a,b){a instanceof String&&(a+="");var c=0,d={next:function(){if(c<a.length){var e=c++;return{value:b(e,a[e]),done:!1}}d.next=function(){return{done:!0,value:void 0}};
return d.next()}};
d[Symbol.iterator]=function(){return d};
return d}
t("Array.prototype.keys",function(a){return a?a:function(){return Ba(this,function(b){return b})}});
t("Array.prototype.values",function(a){return a?a:function(){return Ba(this,function(b,c){return c})}});
function A(a,b){return Object.prototype.hasOwnProperty.call(a,b)}
var Ca="function"==typeof Object.assign?Object.assign:function(a,b){for(var c=1;c<arguments.length;c++){var d=arguments[c];if(d)for(var e in d)A(d,e)&&(a[e]=d[e])}return a};
t("Object.assign",function(a){return a||Ca});
t("Promise",function(a){function b(g){this.g=0;this.h=void 0;this.f=[];var k=this.i();try{g(k.resolve,k.reject)}catch(h){k.reject(h)}}
function c(){this.f=null}
function d(g){return g instanceof b?g:new b(function(k){k(g)})}
if(a)return a;c.prototype.g=function(g){if(null==this.f){this.f=[];var k=this;this.h(function(){k.j()})}this.f.push(g)};
var e=da.setTimeout;c.prototype.h=function(g){e(g,0)};
c.prototype.j=function(){for(;this.f&&this.f.length;){var g=this.f;this.f=[];for(var k=0;k<g.length;++k){var h=g[k];g[k]=null;try{h()}catch(l){this.i(l)}}}this.f=null};
c.prototype.i=function(g){this.h(function(){throw g;})};
b.prototype.i=function(){function g(l){return function(m){h||(h=!0,l.call(k,m))}}
var k=this,h=!1;return{resolve:g(this.G),reject:g(this.j)}};
b.prototype.G=function(g){if(g===this)this.j(new TypeError("A Promise cannot resolve to itself"));else if(g instanceof b)this.ra(g);else{a:switch(typeof g){case "object":var k=null!=g;break a;case "function":k=!0;break a;default:k=!1}k?this.B(g):this.l(g)}};
b.prototype.B=function(g){var k=void 0;try{k=g.then}catch(h){this.j(h);return}"function"==typeof k?this.fa(k,g):this.l(g)};
b.prototype.j=function(g){this.m(2,g)};
b.prototype.l=function(g){this.m(1,g)};
b.prototype.m=function(g,k){if(0!=this.g)throw Error("Cannot settle("+g+", "+k+"): Promise already settled in state"+this.g);this.g=g;this.h=k;this.s()};
b.prototype.s=function(){if(null!=this.f){for(var g=0;g<this.f.length;++g)f.g(this.f[g]);this.f=null}};
var f=new c;b.prototype.ra=function(g){var k=this.i();g.H(k.resolve,k.reject)};
b.prototype.fa=function(g,k){var h=this.i();try{g.call(k,h.resolve,h.reject)}catch(l){h.reject(l)}};
b.prototype.then=function(g,k){function h(r,p){return"function"==typeof r?function(v){try{l(r(v))}catch(y){m(y)}}:p}
var l,m,n=new b(function(r,p){l=r;m=p});
this.H(h(g,l),h(k,m));return n};
b.prototype["catch"]=function(g){return this.then(void 0,g)};
b.prototype.H=function(g,k){function h(){switch(l.g){case 1:g(l.h);break;case 2:k(l.h);break;default:throw Error("Unexpected state: "+l.g);}}
var l=this;null==this.f?f.g(h):this.f.push(h)};
b.resolve=d;b.reject=function(g){return new b(function(k,h){h(g)})};
b.race=function(g){return new b(function(k,h){for(var l=u(g),m=l.next();!m.done;m=l.next())d(m.value).H(k,h)})};
b.all=function(g){var k=u(g),h=k.next();return h.done?d([]):new b(function(l,m){function n(v){return function(y){r[v]=y;p--;0==p&&l(r)}}
var r=[],p=0;do r.push(void 0),p++,d(h.value).H(n(r.length-1),m),h=k.next();while(!h.done)})};
return b});
t("Object.setPrototypeOf",function(a){return a||ma});
t("Array.prototype.entries",function(a){return a?a:function(){return Ba(this,function(b,c){return[b,c]})}});
t("WeakMap",function(a){function b(h){this.f=(k+=Math.random()+1).toString();if(h){h=u(h);for(var l;!(l=h.next()).done;)l=l.value,this.set(l[0],l[1])}}
function c(){}
function d(h){var l=typeof h;return"object"===l&&null!==h||"function"===l}
function e(h){if(!A(h,g)){var l=new c;ba(h,g,{value:l})}}
function f(h){var l=Object[h];l&&(Object[h]=function(m){if(m instanceof c)return m;Object.isExtensible(m)&&e(m);return l(m)})}
if(function(){if(!a||!Object.seal)return!1;try{var h=Object.seal({}),l=Object.seal({}),m=new a([[h,2],[l,3]]);if(2!=m.get(h)||3!=m.get(l))return!1;m["delete"](h);m.set(l,4);return!m.has(h)&&4==m.get(l)}catch(n){return!1}}())return a;
var g="$jscomp_hidden_"+Math.random();f("freeze");f("preventExtensions");f("seal");var k=0;b.prototype.set=function(h,l){if(!d(h))throw Error("Invalid WeakMap key");e(h);if(!A(h,g))throw Error("WeakMap key fail: "+h);h[g][this.f]=l;return this};
b.prototype.get=function(h){return d(h)&&A(h,g)?h[g][this.f]:void 0};
b.prototype.has=function(h){return d(h)&&A(h,g)&&A(h[g],this.f)};
b.prototype["delete"]=function(h){return d(h)&&A(h,g)&&A(h[g],this.f)?delete h[g][this.f]:!1};
return b});
t("Map",function(a){function b(){var k={};return k.previous=k.next=k.head=k}
function c(k,h){var l=k.f;return ea(function(){if(l){for(;l.head!=k.f;)l=l.previous;for(;l.next!=l.head;)return l=l.next,{done:!1,value:h(l)};l=null}return{done:!0,value:void 0}})}
function d(k,h){var l=h&&typeof h;"object"==l||"function"==l?f.has(h)?l=f.get(h):(l=""+ ++g,f.set(h,l)):l="p_"+h;var m=k.g[l];if(m&&A(k.g,l))for(var n=0;n<m.length;n++){var r=m[n];if(h!==h&&r.key!==r.key||h===r.key)return{id:l,list:m,index:n,o:r}}return{id:l,list:m,index:-1,o:void 0}}
function e(k){this.g={};this.f=b();this.size=0;if(k){k=u(k);for(var h;!(h=k.next()).done;)h=h.value,this.set(h[0],h[1])}}
if(function(){if(!a||"function"!=typeof a||!a.prototype.entries||"function"!=typeof Object.seal)return!1;try{var k=Object.seal({x:4}),h=new a(u([[k,"s"]]));if("s"!=h.get(k)||1!=h.size||h.get({x:4})||h.set({x:4},"t")!=h||2!=h.size)return!1;var l=h.entries(),m=l.next();if(m.done||m.value[0]!=k||"s"!=m.value[1])return!1;m=l.next();return m.done||4!=m.value[0].x||"t"!=m.value[1]||!l.next().done?!1:!0}catch(n){return!1}}())return a;
var f=new WeakMap;e.prototype.set=function(k,h){k=0===k?0:k;var l=d(this,k);l.list||(l.list=this.g[l.id]=[]);l.o?l.o.value=h:(l.o={next:this.f,previous:this.f.previous,head:this.f,key:k,value:h},l.list.push(l.o),this.f.previous.next=l.o,this.f.previous=l.o,this.size++);return this};
e.prototype["delete"]=function(k){k=d(this,k);return k.o&&k.list?(k.list.splice(k.index,1),k.list.length||delete this.g[k.id],k.o.previous.next=k.o.next,k.o.next.previous=k.o.previous,k.o.head=null,this.size--,!0):!1};
e.prototype.clear=function(){this.g={};this.f=this.f.previous=b();this.size=0};
e.prototype.has=function(k){return!!d(this,k).o};
e.prototype.get=function(k){return(k=d(this,k).o)&&k.value};
e.prototype.entries=function(){return c(this,function(k){return[k.key,k.value]})};
e.prototype.keys=function(){return c(this,function(k){return k.key})};
e.prototype.values=function(){return c(this,function(k){return k.value})};
e.prototype.forEach=function(k,h){for(var l=this.entries(),m;!(m=l.next()).done;)m=m.value,k.call(h,m[1],m[0],this)};
e.prototype[Symbol.iterator]=e.prototype.entries;var g=0;return e});
t("Object.entries",function(a){return a?a:function(b){var c=[],d;for(d in b)A(b,d)&&c.push([d,b[d]]);return c}});
t("Object.is",function(a){return a?a:function(b,c){return b===c?0!==b||1/b===1/c:b!==b&&c!==c}});
t("Array.prototype.includes",function(a){return a?a:function(b,c){var d=this;d instanceof String&&(d=String(d));var e=d.length,f=c||0;for(0>f&&(f=Math.max(f+e,0));f<e;f++){var g=d[f];if(g===b||Object.is(g,b))return!0}return!1}});
t("String.prototype.includes",function(a){return a?a:function(b,c){return-1!==Aa(this,b,"includes").indexOf(b,c||0)}});
t("Set",function(a){function b(c){this.f=new Map;if(c){c=u(c);for(var d;!(d=c.next()).done;)this.add(d.value)}this.size=this.f.size}
if(function(){if(!a||"function"!=typeof a||!a.prototype.entries||"function"!=typeof Object.seal)return!1;try{var c=Object.seal({x:4}),d=new a(u([c]));if(!d.has(c)||1!=d.size||d.add(c)!=d||1!=d.size||d.add({x:4})!=d||2!=d.size)return!1;var e=d.entries(),f=e.next();if(f.done||f.value[0]!=c||f.value[1]!=c)return!1;f=e.next();return f.done||f.value[0]==c||4!=f.value[0].x||f.value[1]!=f.value[0]?!1:e.next().done}catch(g){return!1}}())return a;
b.prototype.add=function(c){c=0===c?0:c;this.f.set(c,c);this.size=this.f.size;return this};
b.prototype["delete"]=function(c){c=this.f["delete"](c);this.size=this.f.size;return c};
b.prototype.clear=function(){this.f.clear();this.size=0};
b.prototype.has=function(c){return this.f.has(c)};
b.prototype.entries=function(){return this.f.entries()};
b.prototype.values=function(){return this.f.values()};
b.prototype.keys=b.prototype.values;b.prototype[Symbol.iterator]=b.prototype.values;b.prototype.forEach=function(c,d){var e=this;this.f.forEach(function(f){return c.call(d,f,f,e)})};
return b});
var B=this||self;function C(a,b){for(var c=a.split("."),d=b||B,e=0;e<c.length;e++)if(d=d[c[e]],null==d)return null;return d}
function Da(){}
function Ea(a){var b=typeof a;return"object"!=b?b:a?Array.isArray(a)?"array":b:"null"}
function Fa(a){var b=Ea(a);return"array"==b||"object"==b&&"number"==typeof a.length}
function Ga(a){return"function"==Ea(a)}
function Ha(a){var b=typeof a;return"object"==b&&null!=a||"function"==b}
function Ia(a){return Object.prototype.hasOwnProperty.call(a,Ja)&&a[Ja]||(a[Ja]=++Ka)}
var Ja="closure_uid_"+(1E9*Math.random()>>>0),Ka=0;function La(a,b,c){return a.call.apply(a.bind,arguments)}
function Ma(a,b,c){if(!a)throw Error();if(2<arguments.length){var d=Array.prototype.slice.call(arguments,2);return function(){var e=Array.prototype.slice.call(arguments);Array.prototype.unshift.apply(e,d);return a.apply(b,e)}}return function(){return a.apply(b,arguments)}}
function D(a,b,c){Function.prototype.bind&&-1!=Function.prototype.bind.toString().indexOf("native code")?D=La:D=Ma;return D.apply(null,arguments)}
var E=Date.now;function G(a,b){var c=a.split("."),d=B;c[0]in d||"undefined"==typeof d.execScript||d.execScript("var "+c[0]);for(var e;c.length&&(e=c.shift());)c.length||void 0===b?d[e]&&d[e]!==Object.prototype[e]?d=d[e]:d=d[e]={}:d[e]=b}
function H(a,b){function c(){}
c.prototype=b.prototype;a.F=b.prototype;a.prototype=new c;a.prototype.constructor=a}
function Na(a){return a}
;function Oa(a){if(Error.captureStackTrace)Error.captureStackTrace(this,Oa);else{var b=Error().stack;b&&(this.stack=b)}a&&(this.message=String(a))}
H(Oa,Error);Oa.prototype.name="CustomError";var Pa=Array.prototype.indexOf?function(a,b){return Array.prototype.indexOf.call(a,b,void 0)}:function(a,b){if("string"===typeof a)return"string"!==typeof b||1!=b.length?-1:a.indexOf(b,0);
for(var c=0;c<a.length;c++)if(c in a&&a[c]===b)return c;return-1},I=Array.prototype.forEach?function(a,b,c){Array.prototype.forEach.call(a,b,c)}:function(a,b,c){for(var d=a.length,e="string"===typeof a?a.split(""):a,f=0;f<d;f++)f in e&&b.call(c,e[f],f,a)},Qa=Array.prototype.reduce?function(a,b,c){return Array.prototype.reduce.call(a,b,c)}:function(a,b,c){var d=c;
I(a,function(e,f){d=b.call(void 0,d,e,f,a)});
return d};
function Ra(a,b){a:{var c=a.length;for(var d="string"===typeof a?a.split(""):a,e=0;e<c;e++)if(e in d&&b.call(void 0,d[e],e,a)){c=e;break a}c=-1}return 0>c?null:"string"===typeof a?a.charAt(c):a[c]}
function Sa(a){return Array.prototype.concat.apply([],arguments)}
function Ta(a){var b=a.length;if(0<b){for(var c=Array(b),d=0;d<b;d++)c[d]=a[d];return c}return[]}
function Ua(a,b){for(var c=1;c<arguments.length;c++){var d=arguments[c];if(Fa(d)){var e=a.length||0,f=d.length||0;a.length=e+f;for(var g=0;g<f;g++)a[e+g]=d[g]}else a.push(d)}}
;function Va(a){var b=!1,c;return function(){b||(c=a(),b=!0);return c}}
;function Wa(a,b){for(var c in a)b.call(void 0,a[c],c,a)}
function Ya(a){var b=Za,c;for(c in b)if(a.call(void 0,b[c],c,b))return c}
function $a(a,b){for(var c in a)if(!(c in b)||a[c]!==b[c])return!1;for(var d in b)if(!(d in a))return!1;return!0}
function ab(a){var b=Ea(a);if("object"==b||"array"==b){if(Ga(a.clone))return a.clone();b="array"==b?[]:{};for(var c in a)b[c]=ab(a[c]);return b}return a}
var bb="constructor hasOwnProperty isPrototypeOf propertyIsEnumerable toLocaleString toString valueOf".split(" ");function cb(a,b){for(var c,d,e=1;e<arguments.length;e++){d=arguments[e];for(c in d)a[c]=d[c];for(var f=0;f<bb.length;f++)c=bb[f],Object.prototype.hasOwnProperty.call(d,c)&&(a[c]=d[c])}}
;var db;function eb(){if(void 0===db){var a=null,b=B.trustedTypes;if(b&&b.createPolicy){try{a=b.createPolicy("goog#html",{createHTML:Na,createScript:Na,createScriptURL:Na})}catch(c){B.console&&B.console.error(c.message)}db=a}else db=a}return db}
;function fb(a,b){this.g=a===gb&&b||"";this.f=hb}
function ib(a){return a instanceof fb&&a.constructor===fb&&a.f===hb?a.g:"type_error:Const"}
var hb={},gb={};var jb=String.prototype.trim?function(a){return a.trim()}:function(a){return/^[\s\xa0]*([\s\S]*?)[\s\xa0]*$/.exec(a)[1]},kb=/&/g,lb=/</g,mb=/>/g,nb=/"/g,ob=/'/g,pb=/\x00/g,qb=/[\x00&<>"']/;var rb;a:{var sb=B.navigator;if(sb){var tb=sb.userAgent;if(tb){rb=tb;break a}}rb=""}function J(a){return-1!=rb.indexOf(a)}
;function ub(){}
;var vb=J("Opera"),wb=J("Trident")||J("MSIE"),xb=J("Edge"),yb=J("Gecko")&&!(-1!=rb.toLowerCase().indexOf("webkit")&&!J("Edge"))&&!(J("Trident")||J("MSIE"))&&!J("Edge"),zb=-1!=rb.toLowerCase().indexOf("webkit")&&!J("Edge");function Ab(){var a=B.document;return a?a.documentMode:void 0}
var Bb;a:{var Cb="",Db=function(){var a=rb;if(yb)return/rv:([^\);]+)(\)|;)/.exec(a);if(xb)return/Edge\/([\d\.]+)/.exec(a);if(wb)return/\b(?:MSIE|rv)[: ]([^\);]+)(\)|;)/.exec(a);if(zb)return/WebKit\/(\S+)/.exec(a);if(vb)return/(?:Version)[ \/]?(\S+)/.exec(a)}();
Db&&(Cb=Db?Db[1]:"");if(wb){var Eb=Ab();if(null!=Eb&&Eb>parseFloat(Cb)){Bb=String(Eb);break a}}Bb=Cb}var Fb=Bb,Gb;if(B.document&&wb){var Hb=Ab();Gb=Hb?Hb:parseInt(Fb,10)||void 0}else Gb=void 0;var Ib=Gb;var Jb={},Kb=null;var K=window;function Lb(a){var b=C("window.location.href");null==a&&(a='Unknown Error of type "null/undefined"');if("string"===typeof a)return{message:a,name:"Unknown error",lineNumber:"Not available",fileName:b,stack:"Not available"};var c=!1;try{var d=a.lineNumber||a.line||"Not available"}catch(f){d="Not available",c=!0}try{var e=a.fileName||a.filename||a.sourceURL||B.$googDebugFname||b}catch(f){e="Not available",c=!0}return!c&&a.lineNumber&&a.fileName&&a.stack&&a.message&&a.name?a:(b=a.message,null==b&&(a.constructor&&
a.constructor instanceof Function?(a.constructor.name?b=a.constructor.name:(b=a.constructor,Mb[b]?b=Mb[b]:(b=String(b),Mb[b]||(c=/function\s+([^\(]+)/m.exec(b),Mb[b]=c?c[1]:"[Anonymous]"),b=Mb[b])),b='Unknown Error of type "'+b+'"'):b="Unknown Error of unknown type"),{message:b,name:a.name||"UnknownError",lineNumber:d,fileName:e,stack:a.stack||"Not available"})}
var Mb={};function Nb(a){this.f=a||{cookie:""}}
q=Nb.prototype;q.isEnabled=function(){return navigator.cookieEnabled};
q.set=function(a,b,c){var d=!1;if("object"===typeof c){var e=c.Ma;d=c.secure||!1;var f=c.domain||void 0;var g=c.path||void 0;var k=c.W}if(/[;=\s]/.test(a))throw Error('Invalid cookie name "'+a+'"');if(/[;\r\n]/.test(b))throw Error('Invalid cookie value "'+b+'"');void 0===k&&(k=-1);c=f?";domain="+f:"";g=g?";path="+g:"";d=d?";secure":"";k=0>k?"":0==k?";expires="+(new Date(1970,1,1)).toUTCString():";expires="+(new Date(E()+1E3*k)).toUTCString();this.f.cookie=a+"="+b+c+g+k+d+(null!=e?";samesite="+e:"")};
q.get=function(a,b){for(var c=a+"=",d=(this.f.cookie||"").split(";"),e=0,f;e<d.length;e++){f=jb(d[e]);if(0==f.lastIndexOf(c,0))return f.substr(c.length);if(f==a)return""}return b};
q.remove=function(a,b,c){var d=void 0!==this.get(a);this.set(a,"",{W:0,path:b,domain:c});return d};
q.isEmpty=function(){return!this.f.cookie};
q.clear=function(){for(var a=(this.f.cookie||"").split(";"),b=[],c=[],d,e,f=0;f<a.length;f++)e=jb(a[f]),d=e.indexOf("="),-1==d?(b.push(""),c.push(e)):(b.push(e.substring(0,d)),c.push(e.substring(d+1)));for(a=b.length-1;0<=a;a--)this.remove(b[a])};
var Ob=new Nb("undefined"==typeof document?null:document);function Pb(a,b){this.width=a;this.height=b}
q=Pb.prototype;q.clone=function(){return new Pb(this.width,this.height)};
q.aspectRatio=function(){return this.width/this.height};
q.isEmpty=function(){return!(this.width*this.height)};
q.ceil=function(){this.width=Math.ceil(this.width);this.height=Math.ceil(this.height);return this};
q.floor=function(){this.width=Math.floor(this.width);this.height=Math.floor(this.height);return this};
q.round=function(){this.width=Math.round(this.width);this.height=Math.round(this.height);return this};function Qb(a,b){var c,d;var e=document;e=b||e;if(e.querySelectorAll&&e.querySelector&&a)return e.querySelectorAll(a?"."+a:"");if(a&&e.getElementsByClassName){var f=e.getElementsByClassName(a);return f}f=e.getElementsByTagName("*");if(a){var g={};for(c=d=0;e=f[c];c++){var k=e.className,h;if(h="function"==typeof k.split)h=0<=Pa(k.split(/\s+/),a);h&&(g[d++]=e)}g.length=d;return g}return f}
function Rb(){var a=document;var b="IFRAME";"application/xhtml+xml"===a.contentType&&(b=b.toLowerCase());return a.createElement(b)}
function Sb(a,b){for(var c=0;a;){if(b(a))return a;a=a.parentNode;c++}return null}
;var Tb=/^(?:([^:/?#.]+):)?(?:\/\/(?:([^\\/?#]*)@)?([^\\/?#]*?)(?::([0-9]+))?(?=[\\/?#]|$))?([^?#]+)?(?:\?([^#]*))?(?:#([\s\S]*))?$/;function L(a){return a.match(Tb)}
function Ub(a){return a?decodeURI(a):a}
function Vb(a){var b=L(a);a=b[1];var c=b[2],d=b[3];b=b[4];var e="";a&&(e+=a+":");d&&(e+="//",c&&(e+=c+"@"),e+=d,b&&(e+=":"+b));return e}
function Wb(a,b,c){if(Array.isArray(b))for(var d=0;d<b.length;d++)Wb(a,String(b[d]),c);else null!=b&&c.push(a+(""===b?"":"="+encodeURIComponent(String(b))))}
function Xb(a){var b=[],c;for(c in a)Wb(c,a[c],b);return b.join("&")}
var Yb=/#|$/;function Zb(a){var b=$b;if(b)for(var c in b)Object.prototype.hasOwnProperty.call(b,c)&&a.call(void 0,b[c],c,b)}
function ac(){var a=[];Zb(function(b){a.push(b)});
return a}
var $b={sa:"allow-forms",ta:"allow-modals",ua:"allow-orientation-lock",va:"allow-pointer-lock",wa:"allow-popups",xa:"allow-popups-to-escape-sandbox",ya:"allow-presentation",za:"allow-same-origin",Aa:"allow-scripts",Ba:"allow-top-navigation",Ca:"allow-top-navigation-by-user-activation"},bc=Va(function(){return ac()});
function cc(){var a=Rb(),b={};I(bc(),function(c){a.sandbox&&a.sandbox.supports&&a.sandbox.supports(c)&&(b[c]=!0)});
return b}
;function dc(){this.h=this.h;this.i=this.i}
dc.prototype.h=!1;dc.prototype.dispose=function(){this.h||(this.h=!0,this.N())};
dc.prototype.N=function(){if(this.i)for(;this.i.length;)this.i.shift()()};function M(a,b){var c=void 0;return new (c||(c=Promise))(function(d,e){function f(h){try{k(b.next(h))}catch(l){e(l)}}
function g(h){try{k(b["throw"](h))}catch(l){e(l)}}
function k(h){h.done?d(h.value):(new c(function(l){l(h.value)})).then(f,g)}
k((b=b.apply(a,void 0)).next())})}
;var ec=ib(new fb(gb,"//fonts.googleapis.com/css")),fc=eb();fc&&fc.createScriptURL(ec);var gc=(new Date).getTime();function hc(a){if(!a)return"";a=a.split("#")[0].split("?")[0];a=a.toLowerCase();0==a.indexOf("//")&&(a=window.location.protocol+a);/^[\w\-]*:\/\//.test(a)||(a=window.location.href);var b=a.substring(a.indexOf("://")+3),c=b.indexOf("/");-1!=c&&(b=b.substring(0,c));a=a.substring(0,a.indexOf("://"));if("http"!==a&&"https"!==a&&"chrome-extension"!==a&&"file"!==a&&"android-app"!==a&&"chrome-search"!==a&&"chrome-untrusted"!==a&&"chrome"!==a&&"app"!==a)throw Error("Invalid URI scheme in origin: "+a);c="";
var d=b.indexOf(":");if(-1!=d){var e=b.substring(d+1);b=b.substring(0,d);if("http"===a&&"80"!==e||"https"===a&&"443"!==e)c=":"+e}return a+"://"+b+c}
;function ic(){function a(){e[0]=1732584193;e[1]=4023233417;e[2]=2562383102;e[3]=271733878;e[4]=3285377520;m=l=0}
function b(n){for(var r=g,p=0;64>p;p+=4)r[p/4]=n[p]<<24|n[p+1]<<16|n[p+2]<<8|n[p+3];for(p=16;80>p;p++)n=r[p-3]^r[p-8]^r[p-14]^r[p-16],r[p]=(n<<1|n>>>31)&4294967295;n=e[0];var v=e[1],y=e[2],F=e[3],S=e[4];for(p=0;80>p;p++){if(40>p)if(20>p){var oa=F^v&(y^F);var Xa=1518500249}else oa=v^y^F,Xa=1859775393;else 60>p?(oa=v&y|F&(v|y),Xa=2400959708):(oa=v^y^F,Xa=3395469782);oa=((n<<5|n>>>27)&4294967295)+oa+S+Xa+r[p]&4294967295;S=F;F=y;y=(v<<30|v>>>2)&4294967295;v=n;n=oa}e[0]=e[0]+n&4294967295;e[1]=e[1]+v&4294967295;
e[2]=e[2]+y&4294967295;e[3]=e[3]+F&4294967295;e[4]=e[4]+S&4294967295}
function c(n,r){if("string"===typeof n){n=unescape(encodeURIComponent(n));for(var p=[],v=0,y=n.length;v<y;++v)p.push(n.charCodeAt(v));n=p}r||(r=n.length);p=0;if(0==l)for(;p+64<r;)b(n.slice(p,p+64)),p+=64,m+=64;for(;p<r;)if(f[l++]=n[p++],m++,64==l)for(l=0,b(f);p+64<r;)b(n.slice(p,p+64)),p+=64,m+=64}
function d(){var n=[],r=8*m;56>l?c(k,56-l):c(k,64-(l-56));for(var p=63;56<=p;p--)f[p]=r&255,r>>>=8;b(f);for(p=r=0;5>p;p++)for(var v=24;0<=v;v-=8)n[r++]=e[p]>>v&255;return n}
for(var e=[],f=[],g=[],k=[128],h=1;64>h;++h)k[h]=0;var l,m;a();return{reset:a,update:c,digest:d,ga:function(){for(var n=d(),r="",p=0;p<n.length;p++)r+="0123456789ABCDEF".charAt(Math.floor(n[p]/16))+"0123456789ABCDEF".charAt(n[p]%16);return r}}}
;function jc(a,b,c){var d=[],e=[];if(1==(Array.isArray(c)?2:1))return e=[b,a],I(d,function(k){e.push(k)}),kc(e.join(" "));
var f=[],g=[];I(c,function(k){g.push(k.key);f.push(k.value)});
c=Math.floor((new Date).getTime()/1E3);e=0==f.length?[c,b,a]:[f.join(":"),c,b,a];I(d,function(k){e.push(k)});
a=kc(e.join(" "));a=[c,a];0==g.length||a.push(g.join(""));return a.join("_")}
function kc(a){var b=ic();b.update(a);return b.ga().toLowerCase()}
;function lc(a){var b=hc(String(B.location.href)),c;(c=B.__SAPISID||B.__APISID||B.__OVERRIDE_SID)?c=!0:(c=new Nb(document),c=c.get("SAPISID")||c.get("APISID")||c.get("__Secure-3PAPISID")||c.get("SID"),c=!!c);if(c&&(c=(b=0==b.indexOf("https:")||0==b.indexOf("chrome-extension:"))?B.__SAPISID:B.__APISID,c||(c=new Nb(document),c=c.get(b?"SAPISID":"APISID")||c.get("__Secure-3PAPISID")),c)){b=b?"SAPISIDHASH":"APISIDHASH";var d=String(B.location.href);return d&&c&&b?[b,jc(hc(d),c,a||null)].join(" "):null}return null}
;function mc(){this.g=[];this.f=-1}
mc.prototype.set=function(a,b){b=void 0===b?!0:b;0<=a&&52>a&&0===a%1&&this.g[a]!=b&&(this.g[a]=b,this.f=-1)};
mc.prototype.get=function(a){return!!this.g[a]};
function nc(a){-1==a.f&&(a.f=Qa(a.g,function(b,c,d){return c?b+Math.pow(2,d):b},0));
return a.f}
;function oc(a,b){this.h=a;this.i=b;this.g=0;this.f=null}
oc.prototype.get=function(){if(0<this.g){this.g--;var a=this.f;this.f=a.next;a.next=null}else a=this.h();return a};
function pc(a,b){a.i(b);100>a.g&&(a.g++,b.next=a.f,a.f=b)}
;function qc(a){B.setTimeout(function(){throw a;},0)}
var rc;function sc(){var a=B.MessageChannel;"undefined"===typeof a&&"undefined"!==typeof window&&window.postMessage&&window.addEventListener&&!J("Presto")&&(a=function(){var e=Rb();e.style.display="none";document.documentElement.appendChild(e);var f=e.contentWindow;e=f.document;e.open();e.close();var g="callImmediate"+Math.random(),k="file:"==f.location.protocol?"*":f.location.protocol+"//"+f.location.host;e=D(function(h){if(("*"==k||h.origin==k)&&h.data==g)this.port1.onmessage()},this);
f.addEventListener("message",e,!1);this.port1={};this.port2={postMessage:function(){f.postMessage(g,k)}}});
if("undefined"!==typeof a&&!J("Trident")&&!J("MSIE")){var b=new a,c={},d=c;b.port1.onmessage=function(){if(void 0!==c.next){c=c.next;var e=c.U;c.U=null;e()}};
return function(e){d.next={U:e};d=d.next;b.port2.postMessage(0)}}return function(e){B.setTimeout(e,0)}}
;function tc(){this.g=this.f=null}
var vc=new oc(function(){return new uc},function(a){a.reset()});
tc.prototype.add=function(a,b){var c=vc.get();c.set(a,b);this.g?this.g.next=c:this.f=c;this.g=c};
tc.prototype.remove=function(){var a=null;this.f&&(a=this.f,this.f=this.f.next,this.f||(this.g=null),a.next=null);return a};
function uc(){this.next=this.scope=this.f=null}
uc.prototype.set=function(a,b){this.f=a;this.scope=b;this.next=null};
uc.prototype.reset=function(){this.next=this.scope=this.f=null};function wc(a,b){xc||yc();zc||(xc(),zc=!0);Ac.add(a,b)}
var xc;function yc(){if(B.Promise&&B.Promise.resolve){var a=B.Promise.resolve(void 0);xc=function(){a.then(Bc)}}else xc=function(){var b=Bc;
!Ga(B.setImmediate)||B.Window&&B.Window.prototype&&!J("Edge")&&B.Window.prototype.setImmediate==B.setImmediate?(rc||(rc=sc()),rc(b)):B.setImmediate(b)}}
var zc=!1,Ac=new tc;function Bc(){for(var a;a=Ac.remove();){try{a.f.call(a.scope)}catch(b){qc(b)}pc(vc,a)}zc=!1}
;function Cc(){this.g=-1}
;function Dc(){this.g=64;this.f=[];this.l=[];this.m=[];this.i=[];this.i[0]=128;for(var a=1;a<this.g;++a)this.i[a]=0;this.j=this.h=0;this.reset()}
H(Dc,Cc);Dc.prototype.reset=function(){this.f[0]=1732584193;this.f[1]=4023233417;this.f[2]=2562383102;this.f[3]=271733878;this.f[4]=3285377520;this.j=this.h=0};
function Ec(a,b,c){c||(c=0);var d=a.m;if("string"===typeof b)for(var e=0;16>e;e++)d[e]=b.charCodeAt(c)<<24|b.charCodeAt(c+1)<<16|b.charCodeAt(c+2)<<8|b.charCodeAt(c+3),c+=4;else for(e=0;16>e;e++)d[e]=b[c]<<24|b[c+1]<<16|b[c+2]<<8|b[c+3],c+=4;for(e=16;80>e;e++){var f=d[e-3]^d[e-8]^d[e-14]^d[e-16];d[e]=(f<<1|f>>>31)&4294967295}b=a.f[0];c=a.f[1];var g=a.f[2],k=a.f[3],h=a.f[4];for(e=0;80>e;e++){if(40>e)if(20>e){f=k^c&(g^k);var l=1518500249}else f=c^g^k,l=1859775393;else 60>e?(f=c&g|k&(c|g),l=2400959708):
(f=c^g^k,l=3395469782);f=(b<<5|b>>>27)+f+h+l+d[e]&4294967295;h=k;k=g;g=(c<<30|c>>>2)&4294967295;c=b;b=f}a.f[0]=a.f[0]+b&4294967295;a.f[1]=a.f[1]+c&4294967295;a.f[2]=a.f[2]+g&4294967295;a.f[3]=a.f[3]+k&4294967295;a.f[4]=a.f[4]+h&4294967295}
Dc.prototype.update=function(a,b){if(null!=a){void 0===b&&(b=a.length);for(var c=b-this.g,d=0,e=this.l,f=this.h;d<b;){if(0==f)for(;d<=c;)Ec(this,a,d),d+=this.g;if("string"===typeof a)for(;d<b;){if(e[f]=a.charCodeAt(d),++f,++d,f==this.g){Ec(this,e);f=0;break}}else for(;d<b;)if(e[f]=a[d],++f,++d,f==this.g){Ec(this,e);f=0;break}}this.h=f;this.j+=b}};
Dc.prototype.digest=function(){var a=[],b=8*this.j;56>this.h?this.update(this.i,56-this.h):this.update(this.i,this.g-(this.h-56));for(var c=this.g-1;56<=c;c--)this.l[c]=b&255,b/=256;Ec(this,this.l);for(c=b=0;5>c;c++)for(var d=24;0<=d;d-=8)a[b]=this.f[c]>>d&255,++b;return a};var Fc="StopIteration"in B?B.StopIteration:{message:"StopIteration",stack:""};function Gc(){}
Gc.prototype.next=function(){throw Fc;};
Gc.prototype.C=function(){return this};
function Hc(a){if(a instanceof Gc)return a;if("function"==typeof a.C)return a.C(!1);if(Fa(a)){var b=0,c=new Gc;c.next=function(){for(;;){if(b>=a.length)throw Fc;if(b in a)return a[b++];b++}};
return c}throw Error("Not implemented");}
function Ic(a,b){if(Fa(a))try{I(a,b,void 0)}catch(c){if(c!==Fc)throw c;}else{a=Hc(a);try{for(;;)b.call(void 0,a.next(),void 0,a)}catch(c){if(c!==Fc)throw c;}}}
function Jc(a){if(Fa(a))return Ta(a);a=Hc(a);var b=[];Ic(a,function(c){b.push(c)});
return b}
;function Kc(a,b){this.h={};this.f=[];this.i=this.g=0;var c=arguments.length;if(1<c){if(c%2)throw Error("Uneven number of arguments");for(var d=0;d<c;d+=2)this.set(arguments[d],arguments[d+1])}else if(a)if(a instanceof Kc)for(c=Lc(a),d=0;d<c.length;d++)this.set(c[d],a.get(c[d]));else for(d in a)this.set(d,a[d])}
function Lc(a){Mc(a);return a.f.concat()}
q=Kc.prototype;q.equals=function(a,b){if(this===a)return!0;if(this.g!=a.g)return!1;var c=b||Nc;Mc(this);for(var d,e=0;d=this.f[e];e++)if(!c(this.get(d),a.get(d)))return!1;return!0};
function Nc(a,b){return a===b}
q.isEmpty=function(){return 0==this.g};
q.clear=function(){this.h={};this.i=this.g=this.f.length=0};
q.remove=function(a){return Object.prototype.hasOwnProperty.call(this.h,a)?(delete this.h[a],this.g--,this.i++,this.f.length>2*this.g&&Mc(this),!0):!1};
function Mc(a){if(a.g!=a.f.length){for(var b=0,c=0;b<a.f.length;){var d=a.f[b];Object.prototype.hasOwnProperty.call(a.h,d)&&(a.f[c++]=d);b++}a.f.length=c}if(a.g!=a.f.length){var e={};for(c=b=0;b<a.f.length;)d=a.f[b],Object.prototype.hasOwnProperty.call(e,d)||(a.f[c++]=d,e[d]=1),b++;a.f.length=c}}
q.get=function(a,b){return Object.prototype.hasOwnProperty.call(this.h,a)?this.h[a]:b};
q.set=function(a,b){Object.prototype.hasOwnProperty.call(this.h,a)||(this.g++,this.f.push(a),this.i++);this.h[a]=b};
q.forEach=function(a,b){for(var c=Lc(this),d=0;d<c.length;d++){var e=c[d],f=this.get(e);a.call(b,f,e,this)}};
q.clone=function(){return new Kc(this)};
q.C=function(a){Mc(this);var b=0,c=this.i,d=this,e=new Gc;e.next=function(){if(c!=d.i)throw Error("The map has changed since the iterator was created");if(b>=d.f.length)throw Fc;var f=d.f[b++];return a?f:d.h[f]};
return e};var Oc=B.JSON.stringify;function N(a){this.f=0;this.m=void 0;this.i=this.g=this.h=null;this.j=this.l=!1;if(a!=Da)try{var b=this;a.call(void 0,function(c){Pc(b,2,c)},function(c){Pc(b,3,c)})}catch(c){Pc(this,3,c)}}
function Qc(){this.next=this.context=this.onRejected=this.g=this.f=null;this.h=!1}
Qc.prototype.reset=function(){this.context=this.onRejected=this.g=this.f=null;this.h=!1};
var Rc=new oc(function(){return new Qc},function(a){a.reset()});
function Sc(a,b,c){var d=Rc.get();d.g=a;d.onRejected=b;d.context=c;return d}
function Tc(a){if(a instanceof N)return a;var b=new N(Da);Pc(b,2,a);return b}
N.prototype.then=function(a,b,c){return Uc(this,Ga(a)?a:null,Ga(b)?b:null,c)};
N.prototype.$goog_Thenable=!0;N.prototype.cancel=function(a){if(0==this.f){var b=new Vc(a);wc(function(){Wc(this,b)},this)}};
function Wc(a,b){if(0==a.f)if(a.h){var c=a.h;if(c.g){for(var d=0,e=null,f=null,g=c.g;g&&(g.h||(d++,g.f==a&&(e=g),!(e&&1<d)));g=g.next)e||(f=g);e&&(0==c.f&&1==d?Wc(c,b):(f?(d=f,d.next==c.i&&(c.i=d),d.next=d.next.next):Xc(c),Yc(c,e,3,b)))}a.h=null}else Pc(a,3,b)}
function Zc(a,b){a.g||2!=a.f&&3!=a.f||$c(a);a.i?a.i.next=b:a.g=b;a.i=b}
function Uc(a,b,c,d){var e=Sc(null,null,null);e.f=new N(function(f,g){e.g=b?function(k){try{var h=b.call(d,k);f(h)}catch(l){g(l)}}:f;
e.onRejected=c?function(k){try{var h=c.call(d,k);void 0===h&&k instanceof Vc?g(k):f(h)}catch(l){g(l)}}:g});
e.f.h=a;Zc(a,e);return e.f}
N.prototype.B=function(a){this.f=0;Pc(this,2,a)};
N.prototype.G=function(a){this.f=0;Pc(this,3,a)};
function Pc(a,b,c){if(0==a.f){a===c&&(b=3,c=new TypeError("Promise cannot resolve to itself"));a.f=1;a:{var d=c,e=a.B,f=a.G;if(d instanceof N){Zc(d,Sc(e||Da,f||null,a));var g=!0}else{if(d)try{var k=!!d.$goog_Thenable}catch(l){k=!1}else k=!1;if(k)d.then(e,f,a),g=!0;else{if(Ha(d))try{var h=d.then;if(Ga(h)){ad(d,h,e,f,a);g=!0;break a}}catch(l){f.call(a,l);g=!0;break a}g=!1}}}g||(a.m=c,a.f=b,a.h=null,$c(a),3!=b||c instanceof Vc||bd(a,c))}}
function ad(a,b,c,d,e){function f(h){k||(k=!0,d.call(e,h))}
function g(h){k||(k=!0,c.call(e,h))}
var k=!1;try{b.call(a,g,f)}catch(h){f(h)}}
function $c(a){a.l||(a.l=!0,wc(a.s,a))}
function Xc(a){var b=null;a.g&&(b=a.g,a.g=b.next,b.next=null);a.g||(a.i=null);return b}
N.prototype.s=function(){for(var a;a=Xc(this);)Yc(this,a,this.f,this.m);this.l=!1};
function Yc(a,b,c,d){if(3==c&&b.onRejected&&!b.h)for(;a&&a.j;a=a.h)a.j=!1;if(b.f)b.f.h=null,cd(b,c,d);else try{b.h?b.g.call(b.context):cd(b,c,d)}catch(e){dd.call(null,e)}pc(Rc,b)}
function cd(a,b,c){2==b?a.g.call(a.context,c):a.onRejected&&a.onRejected.call(a.context,c)}
function bd(a,b){a.j=!0;wc(function(){a.j&&dd.call(null,b)})}
var dd=qc;function Vc(a){Oa.call(this,a)}
H(Vc,Oa);Vc.prototype.name="cancel";function O(a){dc.call(this);this.m=1;this.j=[];this.l=0;this.f=[];this.g={};this.s=!!a}
H(O,dc);q=O.prototype;q.subscribe=function(a,b,c){var d=this.g[a];d||(d=this.g[a]=[]);var e=this.m;this.f[e]=a;this.f[e+1]=b;this.f[e+2]=c;this.m=e+3;d.push(e);return e};
function ed(a,b,c){var d=fd;if(a=d.g[a]){var e=d.f;(a=Ra(a,function(f){return e[f+1]==b&&e[f+2]==c}))&&d.K(a)}}
q.K=function(a){var b=this.f[a];if(b){var c=this.g[b];if(0!=this.l)this.j.push(a),this.f[a+1]=Da;else{if(c){var d=Pa(c,a);0<=d&&Array.prototype.splice.call(c,d,1)}delete this.f[a];delete this.f[a+1];delete this.f[a+2]}}return!!b};
q.R=function(a,b){var c=this.g[a];if(c){for(var d=Array(arguments.length-1),e=1,f=arguments.length;e<f;e++)d[e-1]=arguments[e];if(this.s)for(e=0;e<c.length;e++){var g=c[e];gd(this.f[g+1],this.f[g+2],d)}else{this.l++;try{for(e=0,f=c.length;e<f;e++)g=c[e],this.f[g+1].apply(this.f[g+2],d)}finally{if(this.l--,0<this.j.length&&0==this.l)for(;c=this.j.pop();)this.K(c)}}return 0!=e}return!1};
function gd(a,b,c){wc(function(){a.apply(b,c)})}
q.clear=function(a){if(a){var b=this.g[a];b&&(I(b,this.K,this),delete this.g[a])}else this.f.length=0,this.g={}};
q.N=function(){O.F.N.call(this);this.clear();this.j.length=0};function hd(a){this.f=a}
hd.prototype.set=function(a,b){void 0===b?this.f.remove(a):this.f.set(a,Oc(b))};
hd.prototype.get=function(a){try{var b=this.f.get(a)}catch(c){return}if(null!==b)try{return JSON.parse(b)}catch(c){throw"Storage: Invalid value was encountered";}};
hd.prototype.remove=function(a){this.f.remove(a)};function id(a){this.f=a}
H(id,hd);function jd(a){this.data=a}
function kd(a){return void 0===a||a instanceof jd?a:new jd(a)}
id.prototype.set=function(a,b){id.F.set.call(this,a,kd(b))};
id.prototype.g=function(a){a=id.F.get.call(this,a);if(void 0===a||a instanceof Object)return a;throw"Storage: Invalid value was encountered";};
id.prototype.get=function(a){if(a=this.g(a)){if(a=a.data,void 0===a)throw"Storage: Invalid value was encountered";}else a=void 0;return a};function ld(a){this.f=a}
H(ld,id);ld.prototype.set=function(a,b,c){if(b=kd(b)){if(c){if(c<E()){ld.prototype.remove.call(this,a);return}b.expiration=c}b.creation=E()}ld.F.set.call(this,a,b)};
ld.prototype.g=function(a){var b=ld.F.g.call(this,a);if(b){var c=b.creation,d=b.expiration;if(d&&d<E()||c&&c>E())ld.prototype.remove.call(this,a);else return b}};function md(){}
;function nd(){}
H(nd,md);nd.prototype.clear=function(){var a=Jc(this.C(!0)),b=this;I(a,function(c){b.remove(c)})};function od(a){this.f=a}
H(od,nd);q=od.prototype;q.isAvailable=function(){if(!this.f)return!1;try{return this.f.setItem("__sak","1"),this.f.removeItem("__sak"),!0}catch(a){return!1}};
q.set=function(a,b){try{this.f.setItem(a,b)}catch(c){if(0==this.f.length)throw"Storage mechanism: Storage disabled";throw"Storage mechanism: Quota exceeded";}};
q.get=function(a){a=this.f.getItem(a);if("string"!==typeof a&&null!==a)throw"Storage mechanism: Invalid value was encountered";return a};
q.remove=function(a){this.f.removeItem(a)};
q.C=function(a){var b=0,c=this.f,d=new Gc;d.next=function(){if(b>=c.length)throw Fc;var e=c.key(b++);if(a)return e;e=c.getItem(e);if("string"!==typeof e)throw"Storage mechanism: Invalid value was encountered";return e};
return d};
q.clear=function(){this.f.clear()};
q.key=function(a){return this.f.key(a)};function pd(){var a=null;try{a=window.localStorage||null}catch(b){}this.f=a}
H(pd,od);function qd(a,b){this.g=a;this.f=null;if(wb&&!(9<=Number(Ib))){rd||(rd=new Kc);this.f=rd.get(a);this.f||(b?this.f=document.getElementById(b):(this.f=document.createElement("userdata"),this.f.addBehavior("#default#userData"),document.body.appendChild(this.f)),rd.set(a,this.f));try{this.f.load(this.g)}catch(c){this.f=null}}}
H(qd,nd);var sd={".":".2E","!":".21","~":".7E","*":".2A","'":".27","(":".28",")":".29","%":"."},rd=null;function td(a){return"_"+encodeURIComponent(a).replace(/[.!~*'()%]/g,function(b){return sd[b]})}
q=qd.prototype;q.isAvailable=function(){return!!this.f};
q.set=function(a,b){this.f.setAttribute(td(a),b);ud(this)};
q.get=function(a){a=this.f.getAttribute(td(a));if("string"!==typeof a&&null!==a)throw"Storage mechanism: Invalid value was encountered";return a};
q.remove=function(a){this.f.removeAttribute(td(a));ud(this)};
q.C=function(a){var b=0,c=this.f.XMLDocument.documentElement.attributes,d=new Gc;d.next=function(){if(b>=c.length)throw Fc;var e=c[b++];if(a)return decodeURIComponent(e.nodeName.replace(/\./g,"%")).substr(1);e=e.nodeValue;if("string"!==typeof e)throw"Storage mechanism: Invalid value was encountered";return e};
return d};
q.clear=function(){for(var a=this.f.XMLDocument.documentElement,b=a.attributes.length;0<b;b--)a.removeAttribute(a.attributes[b-1].nodeName);ud(this)};
function ud(a){try{a.f.save(a.g)}catch(b){throw"Storage mechanism: Quota exceeded";}}
;function vd(a,b){this.g=a;this.f=b+"::"}
H(vd,nd);vd.prototype.set=function(a,b){this.g.set(this.f+a,b)};
vd.prototype.get=function(a){return this.g.get(this.f+a)};
vd.prototype.remove=function(a){this.g.remove(this.f+a)};
vd.prototype.C=function(a){var b=this.g.C(!0),c=this,d=new Gc;d.next=function(){for(var e=b.next();e.substr(0,c.f.length)!=c.f;)e=b.next();return a?e.substr(c.f.length):c.g.get(e)};
return d};var P=window.yt&&window.yt.config_||window.ytcfg&&window.ytcfg.data_||{};G("yt.config_",P);function wd(a){var b=arguments;1<b.length?P[b[0]]=b[1]:1===b.length&&Object.assign(P,b[0])}
function Q(a,b){return a in P?P[a]:b}
;var xd=[];function yd(a){xd.forEach(function(b){return b(a)})}
function zd(a){return a&&window.yterr?function(){try{return a.apply(this,arguments)}catch(b){Ad(b),yd(b)}}:a}
function Ad(a){var b=C("yt.logging.errors.log");b?b(a,"ERROR",void 0,void 0,void 0):(b=Q("ERRORS",[]),b.push([a,"ERROR",void 0,void 0,void 0]),wd("ERRORS",b))}
function Bd(a){var b=C("yt.logging.errors.log");b?b(a,"WARNING",void 0,void 0,void 0):(b=Q("ERRORS",[]),b.push([a,"WARNING",void 0,void 0,void 0]),wd("ERRORS",b))}
;var Cd=0;G("ytDomDomGetNextId",C("ytDomDomGetNextId")||function(){return++Cd});var Dd={stopImmediatePropagation:1,stopPropagation:1,preventMouseEvent:1,preventManipulation:1,preventDefault:1,layerX:1,layerY:1,screenX:1,screenY:1,scale:1,rotation:1,webkitMovementX:1,webkitMovementY:1};
function Ed(a){this.type="";this.state=this.source=this.data=this.currentTarget=this.relatedTarget=this.target=null;this.charCode=this.keyCode=0;this.metaKey=this.shiftKey=this.ctrlKey=this.altKey=!1;this.clientY=this.clientX=0;this.changedTouches=this.touches=null;try{if(a=a||window.event){this.event=a;for(var b in a)b in Dd||(this[b]=a[b]);var c=a.target||a.srcElement;c&&3==c.nodeType&&(c=c.parentNode);this.target=c;var d=a.relatedTarget;if(d)try{d=d.nodeName?d:null}catch(e){d=null}else"mouseover"==
this.type?d=a.fromElement:"mouseout"==this.type&&(d=a.toElement);this.relatedTarget=d;this.clientX=void 0!=a.clientX?a.clientX:a.pageX;this.clientY=void 0!=a.clientY?a.clientY:a.pageY;this.keyCode=a.keyCode?a.keyCode:a.which;this.charCode=a.charCode||("keypress"==this.type?this.keyCode:0);this.altKey=a.altKey;this.ctrlKey=a.ctrlKey;this.shiftKey=a.shiftKey;this.metaKey=a.metaKey}}catch(e){}}
Ed.prototype.preventDefault=function(){this.event&&(this.event.returnValue=!1,this.event.preventDefault&&this.event.preventDefault())};
Ed.prototype.stopPropagation=function(){this.event&&(this.event.cancelBubble=!0,this.event.stopPropagation&&this.event.stopPropagation())};
Ed.prototype.stopImmediatePropagation=function(){this.event&&(this.event.cancelBubble=!0,this.event.stopImmediatePropagation&&this.event.stopImmediatePropagation())};var Za=B.ytEventsEventsListeners||{};G("ytEventsEventsListeners",Za);var Fd=B.ytEventsEventsCounter||{count:0};G("ytEventsEventsCounter",Fd);
function Gd(a,b,c,d){d=void 0===d?{}:d;a.addEventListener&&("mouseenter"!=b||"onmouseenter"in document?"mouseleave"!=b||"onmouseenter"in document?"mousewheel"==b&&"MozBoxSizing"in document.documentElement.style&&(b="MozMousePixelScroll"):b="mouseout":b="mouseover");return Ya(function(e){var f="boolean"===typeof e[4]&&e[4]==!!d,g=Ha(e[4])&&Ha(d)&&$a(e[4],d);return!!e.length&&e[0]==a&&e[1]==b&&e[2]==c&&(f||g)})}
function Hd(a){a&&("string"==typeof a&&(a=[a]),I(a,function(b){if(b in Za){var c=Za[b],d=c[0],e=c[1],f=c[3];c=c[4];d.removeEventListener?Id()||"boolean"===typeof c?d.removeEventListener(e,f,c):d.removeEventListener(e,f,!!c.capture):d.detachEvent&&d.detachEvent("on"+e,f);delete Za[b]}}))}
var Id=Va(function(){var a=!1;try{var b=Object.defineProperty({},"capture",{get:function(){a=!0}});
window.addEventListener("test",null,b)}catch(c){}return a});
function Jd(a,b,c){var d=void 0===d?{}:d;if(a&&(a.addEventListener||a.attachEvent)){var e=Gd(a,b,c,d);if(!e){e=++Fd.count+"";var f=!("mouseenter"!=b&&"mouseleave"!=b||!a.addEventListener||"onmouseenter"in document);var g=f?function(k){k=new Ed(k);if(!Sb(k.relatedTarget,function(h){return h==a}))return k.currentTarget=a,k.type=b,c.call(a,k)}:function(k){k=new Ed(k);
k.currentTarget=a;return c.call(a,k)};
g=zd(g);a.addEventListener?("mouseenter"==b&&f?b="mouseover":"mouseleave"==b&&f?b="mouseout":"mousewheel"==b&&"MozBoxSizing"in document.documentElement.style&&(b="MozMousePixelScroll"),Id()||"boolean"===typeof d?a.addEventListener(b,g,d):a.addEventListener(b,g,!!d.capture)):a.attachEvent("on"+b,g);Za[e]=[a,b,c,g,d]}}}
;function Kd(a,b){"function"===typeof a&&(a=zd(a));return window.setTimeout(a,b)}
function Ld(a){"function"===typeof a&&(a=zd(a));return window.setInterval(a,250)}
;function Md(a){var b=[];Wa(a,function(c,d){var e=encodeURIComponent(String(d)),f;Array.isArray(c)?f=c:f=[c];I(f,function(g){""==g?b.push(e):b.push(e+"="+encodeURIComponent(String(g)))})});
return b.join("&")}
function Nd(a){"?"==a.charAt(0)&&(a=a.substr(1));a=a.split("&");for(var b={},c=0,d=a.length;c<d;c++){var e=a[c].split("=");if(1==e.length&&e[0]||2==e.length)try{var f=decodeURIComponent((e[0]||"").replace(/\+/g," ")),g=decodeURIComponent((e[1]||"").replace(/\+/g," "));f in b?Array.isArray(b[f])?Ua(b[f],g):b[f]=[b[f],g]:b[f]=g}catch(h){if("q"!=e[0]){var k=Error("Error decoding URL component");k.params={key:e[0],value:e[1]};Ad(k)}}}return b}
function Od(a,b,c){var d=a.split("#",2);a=d[0];d=1<d.length?"#"+d[1]:"";var e=a.split("?",2);a=e[0];e=Nd(e[1]||"");for(var f in b)!c&&null!==e&&f in e||(e[f]=b[f]);b=a;a=Xb(e);a?(c=b.indexOf("#"),0>c&&(c=b.length),f=b.indexOf("?"),0>f||f>c?(f=c,e=""):e=b.substring(f+1,c),b=[b.substr(0,f),e,b.substr(c)],c=b[1],b[1]=a?c?c+"&"+a:a:c,a=b[0]+(b[1]?"?"+b[1]:"")+b[2]):a=b;return a+d}
;var Pd={};function Qd(a){return Pd[a]||(Pd[a]=String(a).replace(/\-([a-z])/g,function(b,c){return c.toUpperCase()}))}
;var Rd={},Sd=[],fd=new O,Td={};function Ud(){for(var a=u(Sd),b=a.next();!b.done;b=a.next())b=b.value,b()}
function Vd(a,b){b||(b=document);var c=Ta(b.getElementsByTagName("yt:"+a));var d="yt-"+a;var e=b||document;d=e.querySelectorAll&&e.querySelector?e.querySelectorAll("."+d):Qb(d,b);d=Ta(d);return Sa(c,d)}
function R(a,b){var c;"yt:"==a.tagName.toLowerCase().substr(0,3)?c=a.getAttribute(b):c=a?a.dataset?a.dataset[Qd(b)]:a.getAttribute("data-"+b):null;return c}
function Wd(a,b){fd.R.apply(fd,arguments)}
;function Xd(a){this.g=a||{};this.h=this.f=!1;a=document.getElementById("www-widgetapi-script");if(this.f=!!("https:"==document.location.protocol||a&&0==a.src.indexOf("https:"))){a=[this.g,window.YTConfig||{}];for(var b=0;b<a.length;b++)a[b].host&&(a[b].host=a[b].host.replace("http://","https://"))}}
function T(a,b){for(var c=[a.g,window.YTConfig||{}],d=0;d<c.length;d++){var e=c[d][b];if(void 0!=e)return e}return null}
function Yd(a,b,c){Zd||(Zd={},Jd(window,"message",D(a.i,a)));Zd[c]=b}
Xd.prototype.i=function(a){if(a.origin==T(this,"host")||a.origin==T(this,"host").replace(/^http:/,"https:")){try{var b=JSON.parse(a.data)}catch(c){return}this.h=!0;this.f||0!=a.origin.indexOf("https:")||(this.f=!0);if(a=Zd[b.id])a.s=!0,a.s&&(I(a.m,a.T,a),a.m.length=0),a.da(b)}};
var Zd=null;function U(a){a=$d(a);return"string"===typeof a&&"false"===a?!1:!!a}
function ae(a,b){var c=$d(a);return void 0===c&&void 0!==b?b:Number(c||0)}
function $d(a){var b=Q("EXPERIMENTS_FORCED_FLAGS",{});return void 0!==b[a]?b[a]:Q("EXPERIMENT_FLAGS",{})[a]}
;function be(){}
function ce(a,b){return de(a,0,b)}
;function ee(){}
w(ee,be);function de(a,b,c){isNaN(c)&&(c=void 0);var d=C("yt.scheduler.instance.addJob");return d?d(a,b,c):void 0===c?(a(),NaN):Kd(a,c||0)}
ee.prototype.start=function(){var a=C("yt.scheduler.instance.start");a&&a()};
ee.f=void 0;ee.g=function(){ee.f||(ee.f=new ee)};
ee.g();var fe=B.ytPubsubPubsubInstance||new O;O.prototype.subscribe=O.prototype.subscribe;O.prototype.unsubscribeByKey=O.prototype.K;O.prototype.publish=O.prototype.R;O.prototype.clear=O.prototype.clear;G("ytPubsubPubsubInstance",fe);G("ytPubsubPubsubSubscribedKeys",B.ytPubsubPubsubSubscribedKeys||{});G("ytPubsubPubsubTopicToKeys",B.ytPubsubPubsubTopicToKeys||{});G("ytPubsubPubsubIsSynchronous",B.ytPubsubPubsubIsSynchronous||{});var V=window,W=V.ytcsi&&V.ytcsi.now?V.ytcsi.now:V.performance&&V.performance.timing&&V.performance.now&&V.performance.timing.navigationStart?function(){return V.performance.timing.navigationStart+V.performance.now()}:function(){return(new Date).getTime()};var ge=ae("initial_gel_batch_timeout",1E3),he=Math.pow(2,16)-1,ie=null,je=0,ke=void 0,le=0,me=0,ne=0,oe=!0,pe=B.ytLoggingTransportLogPayloadsQueue_||{};G("ytLoggingTransportLogPayloadsQueue_",pe);var qe=B.ytLoggingTransportGELQueue_||new Map;G("ytLoggingTransportGELQueue_",qe);var re=B.ytLoggingTransportTokensToCttTargetIds_||{};G("ytLoggingTransportTokensToCttTargetIds_",re);
function se(){window.clearTimeout(le);window.clearTimeout(me);me=0;ke&&ke.isReady()?(te(qe),"log_event"in pe&&te(Object.entries(pe.log_event)),qe.clear(),delete pe.log_event):ue()}
function ue(){U("web_gel_timeout_cap")&&!me&&(me=Kd(se,6E4));window.clearTimeout(le);var a=Q("LOGGING_BATCH_TIMEOUT",ae("web_gel_debounce_ms",1E4));U("shorten_initial_gel_batch_timeout")&&oe&&(a=ge);le=Kd(se,a)}
function te(a){var b=ke,c=Math.round(W());a=u(a);for(var d=a.next();!d.done;d=a.next()){var e=u(d.value);d=e.next().value;var f=e.next().value;e=ab({context:ve(b.f||we())});e.events=f;(f=re[d])&&xe(e,d,f);delete re[d];ye(e,c);ze(b,"log_event",e,{retry:!0,onSuccess:function(){je=Math.round(W()-c)}});
oe=!1}}
function ye(a,b){a.requestTimeMs=String(b);U("unsplit_gel_payloads_in_logs")&&(a.unsplitGelPayloadsInLogs=!0);var c=Q("EVENT_ID",void 0);if(c){var d=Q("BATCH_CLIENT_COUNTER",void 0)||0;!d&&U("web_client_counter_random_seed")&&(d=Math.floor(Math.random()*he/2));d++;d>he&&(d=1);wd("BATCH_CLIENT_COUNTER",d);c={serializedEventId:c,clientCounter:String(d)};a.serializedClientEventId=c;ie&&je&&U("log_gel_rtt_web")&&(a.previousBatchInfo={serializedClientEventId:ie,roundtripMs:String(je)});ie=c;je=0}}
function xe(a,b,c){if(c.videoId)var d="VIDEO";else if(c.playlistId)d="PLAYLIST";else return;a.credentialTransferTokenTargetId=c;a.context=a.context||{};a.context.user=a.context.user||{};a.context.user.credentialTransferTokens=[{token:b,scope:d}]}
;var Ae=B.ytLoggingGelSequenceIdObj_||{};G("ytLoggingGelSequenceIdObj_",Ae);function Be(a){var b=Ce;a=void 0===a?C("yt.ads.biscotti.lastId_")||"":a;b=Object.assign(De(b),Ee(b));b.ca_type="image";a&&(b.bid=a);return b}
function De(a){var b={};b.dt=gc;b.flash="0";a:{try{var c=a.f.top.location.href}catch(f){a=2;break a}a=c?c===a.g.location.href?0:1:2}b=(b.frm=a,b);b.u_tz=-(new Date).getTimezoneOffset();var d=void 0===d?K:d;try{var e=d.history.length}catch(f){e=0}b.u_his=e;b.u_java=!!K.navigator&&"unknown"!==typeof K.navigator.javaEnabled&&!!K.navigator.javaEnabled&&K.navigator.javaEnabled();K.screen&&(b.u_h=K.screen.height,b.u_w=K.screen.width,b.u_ah=K.screen.availHeight,b.u_aw=K.screen.availWidth,b.u_cd=K.screen.colorDepth);
K.navigator&&K.navigator.plugins&&(b.u_nplug=K.navigator.plugins.length);K.navigator&&K.navigator.mimeTypes&&(b.u_nmime=K.navigator.mimeTypes.length);return b}
function Ee(a){var b=a.f;try{var c=b.screenX;var d=b.screenY}catch(n){}try{var e=b.outerWidth;var f=b.outerHeight}catch(n){}try{var g=b.innerWidth;var k=b.innerHeight}catch(n){}b=[b.screenLeft,b.screenTop,c,d,b.screen?b.screen.availWidth:void 0,b.screen?b.screen.availTop:void 0,e,f,g,k];c=a.f.top;try{var h=(c||window).document,l="CSS1Compat"==h.compatMode?h.documentElement:h.body;var m=(new Pb(l.clientWidth,l.clientHeight)).round()}catch(n){m=new Pb(-12245933,-12245933)}h=m;m={};l=new mc;B.SVGElement&&
B.document.createElementNS&&l.set(0);c=cc();c["allow-top-navigation-by-user-activation"]&&l.set(1);c["allow-popups-to-escape-sandbox"]&&l.set(2);B.crypto&&B.crypto.subtle&&l.set(3);B.TextDecoder&&B.TextEncoder&&l.set(4);l=nc(l);m.bc=l;m.bih=h.height;m.biw=h.width;m.brdim=b.join();a=a.g;return m.vis={visible:1,hidden:2,prerender:3,preview:4,unloaded:5}[a.visibilityState||a.webkitVisibilityState||a.mozVisibilityState||""]||0,m.wgl=!!K.WebGLRenderingContext,m}
var Ce=new function(){var a=window.document;this.f=window;this.g=a};
G("yt.ads_.signals_.getAdSignalsString",function(a){return Md(Be(a))});E();var Fe="XMLHttpRequest"in B?function(){return new XMLHttpRequest}:null;
function Ge(){if(!Fe)return null;var a=Fe();return"open"in a?a:null}
;var He={Authorization:"AUTHORIZATION","X-Goog-Visitor-Id":"SANDBOXED_VISITOR_ID","X-YouTube-Client-Name":"INNERTUBE_CONTEXT_CLIENT_NAME","X-YouTube-Client-Version":"INNERTUBE_CONTEXT_CLIENT_VERSION","X-YouTube-Device":"DEVICE","X-Youtube-Identity-Token":"ID_TOKEN","X-YouTube-Page-CL":"PAGE_CL","X-YouTube-Page-Label":"PAGE_BUILD_LABEL","X-YouTube-Variants-Checksum":"VARIANTS_CHECKSUM"},Ie="app debugcss debugjs expflag force_ad_params force_viral_ad_response_params forced_experiments innertube_snapshots innertube_goldens internalcountrycode internalipoverride absolute_experiments conditional_experiments sbb sr_bns_address".split(" "),
Je=!1;
function Ke(a,b){b=void 0===b?{}:b;if(!c)var c=window.location.href;var d=L(a)[1]||null,e=Ub(L(a)[3]||null);d&&e?(d=c,c=L(a),d=L(d),c=c[3]==d[3]&&c[1]==d[1]&&c[4]==d[4]):c=e?Ub(L(c)[3]||null)==e&&(Number(L(c)[4]||null)||null)==(Number(L(a)[4]||null)||null):!0;d=U("web_ajax_ignore_global_headers_if_set");for(var f in He)e=Q(He[f]),!e||!c&&!Le(a,f)||d&&void 0!==b[f]||(b[f]=e);if(c||Le(a,"X-YouTube-Utc-Offset"))b["X-YouTube-Utc-Offset"]=String(-(new Date).getTimezoneOffset());(c||Le(a,"X-YouTube-Time-Zone"))&&(f=
"undefined"!=typeof Intl?(new Intl.DateTimeFormat).resolvedOptions().timeZone:null)&&(b["X-YouTube-Time-Zone"]=f);if(c||Le(a,"X-YouTube-Ad-Signals"))b["X-YouTube-Ad-Signals"]=Md(Be(void 0));return b}
function Me(a){var b=window.location.search,c=Ub(L(a)[3]||null),d=Ub(L(a)[5]||null);d=(c=c&&(c.endsWith("youtube.com")||c.endsWith("youtube-nocookie.com")))&&d&&d.startsWith("/api/");if(!c||d)return a;var e=Nd(b),f={};I(Ie,function(g){e[g]&&(f[g]=e[g])});
return Od(a,f||{},!1)}
function Le(a,b){var c=Q("CORS_HEADER_WHITELIST")||{},d=Ub(L(a)[3]||null);return d?(c=c[d])?0<=Pa(c,b):!1:!0}
function Ne(a,b){if(window.fetch&&"XML"!=b.format){var c={method:b.method||"GET",credentials:"same-origin"};b.headers&&(c.headers=b.headers);a=Oe(a,b);var d=Pe(a,b);d&&(c.body=d);b.withCredentials&&(c.credentials="include");var e=!1,f;fetch(a,c).then(function(g){if(!e){e=!0;f&&window.clearTimeout(f);var k=g.ok,h=function(l){l=l||{};var m=b.context||B;k?b.onSuccess&&b.onSuccess.call(m,l,g):b.onError&&b.onError.call(m,l,g);b.O&&b.O.call(m,l,g)};
"JSON"==(b.format||"JSON")&&(k||400<=g.status&&500>g.status)?g.json().then(h,function(){h(null)}):h(null)}});
b.aa&&0<b.timeout&&(f=Kd(function(){e||(e=!0,window.clearTimeout(f),b.aa.call(b.context||B))},b.timeout))}else Qe(a,b)}
function Qe(a,b){var c=b.format||"JSON";a=Oe(a,b);var d=Pe(a,b),e=!1,f=Re(a,function(h){if(!e){e=!0;k&&window.clearTimeout(k);a:switch(h&&"status"in h?h.status:-1){case 200:case 201:case 202:case 203:case 204:case 205:case 206:case 304:var l=!0;break a;default:l=!1}var m=null,n=400<=h.status&&500>h.status,r=500<=h.status&&600>h.status;if(l||n||r)m=Se(a,c,h,b.Ga);if(l)a:if(h&&204==h.status)l=!0;else{switch(c){case "XML":l=0==parseInt(m&&m.return_code,10);break a;case "RAW":l=!0;break a}l=!!m}m=m||
{};n=b.context||B;l?b.onSuccess&&b.onSuccess.call(n,h,m):b.onError&&b.onError.call(n,h,m);b.O&&b.O.call(n,h,m)}},b.method,d,b.headers,b.responseType,b.withCredentials);
if(b.I&&0<b.timeout){var g=b.I;var k=Kd(function(){e||(e=!0,f.abort(),window.clearTimeout(k),g.call(b.context||B,f))},b.timeout)}}
function Oe(a,b){b.Ka&&(a=document.location.protocol+"//"+document.location.hostname+(document.location.port?":"+document.location.port:"")+a);var c=Q("XSRF_FIELD_NAME",void 0),d=b.qa;d&&(d[c]&&delete d[c],a=Od(a,d||{},!0));return a}
function Pe(a,b){var c=Q("XSRF_FIELD_NAME",void 0),d=Q("XSRF_TOKEN",void 0),e=b.postBody||"",f=b.u,g=Q("XSRF_FIELD_NAME",void 0),k;b.headers&&(k=b.headers["Content-Type"]);b.Ja||Ub(L(a)[3]||null)&&!b.withCredentials&&Ub(L(a)[3]||null)!=document.location.hostname||"POST"!=b.method||k&&"application/x-www-form-urlencoded"!=k||b.u&&b.u[g]||(f||(f={}),f[c]=d);f&&"string"===typeof e&&(e=Nd(e),cb(e,f),e=b.ca&&"JSON"==b.ca?JSON.stringify(e):Xb(e));if(!(c=e)&&(c=f)){a:{for(var h in f){f=!1;break a}f=!0}c=
!f}!Je&&c&&"POST"!=b.method&&(Je=!0,Ad(Error("AJAX request with postData should use POST")));return e}
function Se(a,b,c,d){var e=null;switch(b){case "JSON":try{var f=c.responseText}catch(g){throw d=Error("Error reading responseText"),d.params=a,Bd(d),g;}a=c.getResponseHeader("Content-Type")||"";f&&0<=a.indexOf("json")&&(e=JSON.parse(f));break;case "XML":if(a=(a=c.responseXML)?Te(a):null)e={},I(a.getElementsByTagName("*"),function(g){e[g.tagName]=Ue(g)})}d&&Ve(e);
return e}
function Ve(a){if(Ha(a))for(var b in a){var c;(c="html_content"==b)||(c=b.length-5,c=0<=c&&b.indexOf("_html",c)==c);if(c){c=b;var d=a[b],e=new fb(gb,"HTML that is escaped and sanitized server-side and passed through yt.net.ajax");ib(e);ib(e);e=new ub;var f=eb();f&&f.createHTML(d);a[c]=e}else Ve(a[b])}}
function Te(a){return a?(a=("responseXML"in a?a.responseXML:a).getElementsByTagName("root"))&&0<a.length?a[0]:null:null}
function Ue(a){var b="";I(a.childNodes,function(c){b+=c.nodeValue});
return b}
function Re(a,b,c,d,e,f,g){function k(){4==(h&&"readyState"in h?h.readyState:0)&&b&&zd(b)(h)}
c=void 0===c?"GET":c;d=void 0===d?"":d;var h=Ge();if(!h)return null;"onloadend"in h?h.addEventListener("loadend",k,!1):h.onreadystatechange=k;U("debug_forward_web_query_parameters")&&(a=Me(a));h.open(c,a,!0);f&&(h.responseType=f);g&&(h.withCredentials=!0);c="POST"==c&&(void 0===window.FormData||!(d instanceof FormData));if(e=Ke(a,e))for(var l in e)h.setRequestHeader(l,e[l]),"content-type"==l.toLowerCase()&&(c=!1);c&&h.setRequestHeader("Content-Type","application/x-www-form-urlencoded");h.send(d);
return h}
;function We(){for(var a={},b=u(Object.entries(Nd(Q("DEVICE","")))),c=b.next();!c.done;c=b.next()){var d=u(c.value);c=d.next().value;d=d.next().value;"cbrand"===c?a.deviceMake=d:"cmodel"===c?a.deviceModel=d:"cbr"===c?a.browserName=d:"cbrver"===c?a.browserVersion=d:"cos"===c?a.osName=d:"cosver"===c?a.osVersion=d:"cplatform"===c&&(a.platform=d)}return a}
;function Xe(){return"INNERTUBE_API_KEY"in P&&"INNERTUBE_API_VERSION"in P}
function we(){return{innertubeApiKey:Q("INNERTUBE_API_KEY",void 0),innertubeApiVersion:Q("INNERTUBE_API_VERSION",void 0),ia:Q("INNERTUBE_CONTEXT_CLIENT_CONFIG_INFO"),ja:Q("INNERTUBE_CONTEXT_CLIENT_NAME","WEB"),innertubeContextClientVersion:Q("INNERTUBE_CONTEXT_CLIENT_VERSION",void 0),la:Q("INNERTUBE_CONTEXT_HL",void 0),ka:Q("INNERTUBE_CONTEXT_GL",void 0),ma:Q("INNERTUBE_HOST_OVERRIDE",void 0)||"",oa:!!Q("INNERTUBE_USE_THIRD_PARTY_AUTH",!1),na:!!Q("INNERTUBE_OMIT_API_KEY_WHEN_AUTH_HEADER_IS_PRESENT",
!1)}}
function ve(a){a={client:{hl:a.la,gl:a.ka,clientName:a.ja,clientVersion:a.innertubeContextClientVersion,configInfo:a.ia}};var b=window.devicePixelRatio;b&&1!=b&&(a.client.screenDensityFloat=String(b));b=Q("EXPERIMENTS_TOKEN","");""!==b&&(a.client.experimentsToken=b);b=[];var c=Q("EXPERIMENTS_FORCED_FLAGS",{});for(d in c)b.push({key:d,value:String(c[d])});var d=Q("EXPERIMENT_FLAGS",{});for(var e in d)e.startsWith("force_")&&void 0===c[e]&&b.push({key:e,value:String(d[e])});0<b.length&&(a.request={internalExperimentFlags:b});
Q("DELEGATED_SESSION_ID")&&!U("pageid_as_header_web")&&(a.user={onBehalfOfUser:Q("DELEGATED_SESSION_ID")});a.client=Object.assign(a.client,We());return a}
function Ye(a,b,c){c=void 0===c?{}:c;var d={"X-Goog-Visitor-Id":c.visitorData||Q("VISITOR_DATA","")};if(b&&b.includes("www.youtube-nocookie.com"))return d;(b=c.Fa||Q("AUTHORIZATION"))||(a?b="Bearer "+C("gapi.auth.getToken")().Da:b=lc([]));b&&(d.Authorization=b,d["X-Goog-AuthUser"]=Q("SESSION_INDEX",0),U("pageid_as_header_web")&&(d["X-Goog-PageId"]=Q("DELEGATED_SESSION_ID")));return d}
;function Ze(a){a=Object.assign({},a);delete a.Authorization;var b=lc();if(b){var c=new Dc;c.update(Q("INNERTUBE_API_KEY",void 0));c.update(b);b=c.digest();c=3;Fa(b);void 0===c&&(c=0);if(!Kb){Kb={};for(var d="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789".split(""),e=["+/=","+/","-_=","-_.","-_"],f=0;5>f;f++){var g=d.concat(e[f].split(""));Jb[f]=g;for(var k=0;k<g.length;k++){var h=g[k];void 0===Kb[h]&&(Kb[h]=k)}}}c=Jb[c];d=[];for(e=0;e<b.length;e+=3){var l=b[e],m=(f=e+1<b.length)?
b[e+1]:0;h=(g=e+2<b.length)?b[e+2]:0;k=l>>2;l=(l&3)<<4|m>>4;m=(m&15)<<2|h>>6;h&=63;g||(h=64,f||(m=64));d.push(c[k],c[l],c[m]||"",c[h]||"")}a.hash=d.join("")}return a}
function $e(a){a=Ze(a);var b=new Dc;b.update(JSON.stringify(a,Object.keys(a).sort()));a=b.digest();b="";for(var c=0;c<a.length;c++)b+="0123456789ABCDEF".charAt(Math.floor(a[c]/16))+"0123456789ABCDEF".charAt(a[c]%16);return b}
;function af(){var a=new pd;(a=a.isAvailable()?new vd(a,"yt.innertube"):null)||(a=new qd("yt.innertube"),a=a.isAvailable()?a:null);this.f=a?new ld(a):null;this.g=document.domain||window.location.hostname}
af.prototype.set=function(a,b,c,d){c=c||31104E3;this.remove(a);if(this.f)try{this.f.set(a,b,E()+1E3*c);return}catch(f){}var e="";if(d)try{e=escape(Oc(b))}catch(f){return}else e=escape(b);b=this.g;Ob.set(""+a,e,{W:c,path:"/",domain:void 0===b?"youtube.com":b,secure:!1})};
af.prototype.get=function(a,b){var c=void 0,d=!this.f;if(!d)try{c=this.f.get(a)}catch(e){d=!0}if(d&&(c=Ob.get(""+a,void 0))&&(c=unescape(c),b))try{c=JSON.parse(c)}catch(e){this.remove(a),c=void 0}return c};
af.prototype.remove=function(a){this.f&&this.f.remove(a);var b=this.g;Ob.remove(""+a,"/",void 0===b?"youtube.com":b)};var bf;function cf(){bf||(bf=new af);return bf}
function df(a,b,c,d){if(d)return null;d=cf().get("nextId",!0)||1;var e=cf().get("requests",!0)||{};e[d]={method:a,request:b,authState:Ze(c),requestTime:Math.round(W())};cf().set("nextId",d+1,86400,!0);cf().set("requests",e,86400,!0);return d}
function ef(a){var b=cf().get("requests",!0)||{};delete b[a];cf().set("requests",b,86400,!0)}
function ff(a){var b=cf().get("requests",!0);if(b){for(var c in b){var d=b[c];if(!(6E4>Math.round(W())-d.requestTime)){var e=d.authState,f=Ze(Ye(!1));$a(e,f)&&(e=d.request,"requestTimeMs"in e&&(e.requestTimeMs=Math.round(W())),ze(a,d.method,e,{}));delete b[c]}}cf().set("requests",b,86400,!0)}}
;function gf(){}
;function hf(){var a=Error.call(this,"Transaction was aborted");this.message=a.message;"stack"in a&&(this.stack=a.stack);Object.setPrototypeOf(this,hf.prototype)}
w(hf,Error);function X(a){return new N(function(b,c){function d(){c(a.error);f()}
function e(){b(a.result);f()}
function f(){a.removeEventListener("success",e);a.removeEventListener("error",d)}
a.addEventListener("success",e);a.addEventListener("error",d)})}
;function jf(a){this.f=a}
q=jf.prototype;q.add=function(a,b,c){return this.A([a],"readwrite").f(a).add(b,c)};
q.clear=function(a){return this.A([a],"readwrite").f(a).clear()};
q.close=function(){this.f.close()};
q.count=function(a,b){return this.A([a]).f(a).count(b)};
q.Y=function(a,b){var c=this.f.createObjectStore(a,b);return new kf(c)};
q["delete"]=function(a,b){return this.A([a],"readwrite").f(a)["delete"](b)};
q.get=function(a,b){return this.A([a]).f(a).get(b)};
q.getName=function(){return this.f.name};
q.A=function(a,b){var c=this.f.transaction(a,b);return new lf(c)};
function kf(a){this.f=a}
q=kf.prototype;q.add=function(a,b){return X(this.f.add(a,b))};
q.clear=function(){return X(this.f.clear()).then(function(){})};
q.count=function(a){return X(this.f.count(a))};
q["delete"]=function(a){return X(this.f["delete"](a))};
q.get=function(a){return X(this.f.get(a))};
q.index=function(a){return new mf(this.f.index(a))};
q.getName=function(){return this.f.name};
function lf(a){var b=this;this.g=a;this.h=new Map;this.done=new N(function(c,d){b.g.addEventListener("complete",function(){c()});
b.g.addEventListener("error",function(){d(b.g.error)});
b.g.addEventListener("abort",function(){d(new hf)})})}
lf.prototype.abort=function(){this.g.abort();return this.done};
lf.prototype.f=function(a){a=this.g.objectStore(a);var b=this.h.get(a);b||(b=new kf(a),this.h.set(a,b));return b};
function mf(a){this.f=a}
mf.prototype.count=function(a){return X(this.f.count(a))};
mf.prototype.get=function(a){return X(this.f.get(a))};
mf.prototype.g=function(a,b){var c=this.f.openCursor(a,b);return nf(c)};
function of(a,b){this.request=a;this.f=b}
function nf(a){return X(a).then(function(b){return null===b?null:new of(a,b)})}
of.prototype["delete"]=function(){return X(this.f["delete"]()).then(function(){})};
of.prototype.update=function(a){return X(this.f.update(a))};function pf(){jf.apply(this,arguments)}
w(pf,jf);pf.prototype.Y=function(a,b){var c=this.f.createObjectStore(a,b);return new qf(c)};
pf.prototype.A=function(a,b){var c=this.f.transaction(a,b);return new rf(c)};
function qf(){kf.apply(this,arguments)}
w(qf,kf);qf.prototype.index=function(a){return new sf(this.f.index(a))};
function rf(){lf.apply(this,arguments);this.i=new Map}
w(rf,lf);rf.prototype.f=function(a){a=this.g.objectStore(a);var b=this.i.get(a);b||(b=new qf(a),this.i.set(a,b));return b};
function sf(){mf.apply(this,arguments)}
w(sf,mf);sf.prototype.g=function(a,b){var c=this.f.openCursor(a,b);return tf(c)};
function uf(){of.apply(this,arguments)}
w(uf,of);function tf(a){return X(a).then(function(b){return null===b?null:new uf(a,b)})}
;function vf(a,b,c,d,e){function f(){n||(n=new d(g.result));return n}
var g=void 0!==b?self.indexedDB.open(a,b):self.indexedDB.open(a);var k=c.f,h=c.blocking,l=c.g,m=c.upgrade,n;m&&g.addEventListener("upgradeneeded",function(r){if(null===r.newVersion)throw Error("Invariant: newVersion on IDbVersionChangeEvent is null");if(null===g.transaction)throw Error("Invariant: transaction on IDbOpenDbRequest is null");var p=f(),v=new e(g.transaction);m(p,r.oldVersion,r.newVersion,v)});
k&&g.addEventListener("blocked",function(){k()});
return X(g).then(function(r){h&&r.addEventListener("versionchange",function(){h()});
l&&r.addEventListener("close",function(){l()});
return f()})}
function wf(a){a=void 0===a?{}:a;return vf("LogsDataBase",1,a,jf,lf)}
function xf(a,b){b=void 0===b?{}:b;return vf("yt-idb-test-do-not-use",a,b,pf,rf)}
;var yf,zf=["getAll","getAllKeys","getKey","openKeyCursor"],Af=["getAll","getAllKeys","getKey","openKeyCursor"];
function Bf(){return M(this,function b(){var c,d,e,f,g,k,h,l;return z(b,function(m){switch(m.f){case 1:if(!self.indexedDB)return m["return"](!1);c=u(zf);for(d=c.next();!d.done;d=c.next())if(e=d.value,!IDBObjectStore.prototype[e])return m["return"](!1);f=u(Af);for(d=f.next();!d.done;d=f.next())if(g=d.value,!IDBIndex.prototype[g])return m["return"](!1);if(!IDBObjectStore.prototype.getKey)return m["return"](!1);ra(m);l=!1;return x(m,xf(void 0,{blocking:function(){l=!0;k&&(k.close(),k=void 0)}}),5);
case 5:return k=m.g,x(m,xf(k.f.version+1),6);case 6:return h=m.g,h.close(),h=void 0,m["return"](l);case 3:ta(m);if(k)try{k.close()}catch(n){}if(h)try{h.close()}catch(n){}ua(m);break;case 2:return sa(m),m["return"](!1)}})})}
function Cf(){return void 0!==yf?Tc(yf):new N(function(a){Bf().then(function(b){yf=b;a(b)})})}
;var Df;function Ef(){return M(this,function b(){return z(b,function(c){if(!Df)try{Df=wf({upgrade:function(d,e){1>e&&d.Y("LogsRequestsStore",{keyPath:"id",autoIncrement:!0}).f.createIndex("newRequest",["status","authHash","timestamp"],{unique:!1})}})}catch(d){"VersionError"===d&&Ad(d),Df=wf()}return c["return"](Df)})})}
function Ff(a){return M(this,function c(){var d,e,f,g,k;return z(c,function(h){switch(h.f){case 1:return x(h,Ef(),2);case 2:return d=h.g,e=d.A(["LogsRequestsStore"],"readwrite").f("LogsRequestsStore"),x(h,Gf(),3);case 3:return f=h.g,g=Object.assign(Object.assign({},a),{options:JSON.parse(JSON.stringify(a.options)),Ea:f}),x(h,e.add(g),4);case 4:return k=h.g,h["return"](k)}})})}
function Hf(){return M(this,function b(){var c,d,e,f,g,k,h,l;return z(b,function(m){switch(m.f){case 1:return x(m,Gf(),2);case 2:return c=m.g,d=["NEW",c,0],e=["NEW",c,W()],f=IDBKeyRange.bound(d,e),x(m,Ef(),3);case 3:return g=m.g,k=g.A(["LogsRequestsStore"],"readwrite"),x(m,k.f("LogsRequestsStore").index("newRequest").g(f,"prev"),4);case 4:h=m.g;l=void 0;if(null===h||void 0===h||!h.f.value){m.v(5);break}l=h.f.value;l.status="QUEUED";return x(m,h.update(l),5);case 5:return m["return"](l)}})})}
function If(a){return M(this,function c(){var d,e,f;return z(c,function(g){switch(g.f){case 1:return x(g,Ef(),2);case 2:return d=g.g,e=d.A(["LogsRequestsStore"],"readwrite").f("LogsRequestsStore"),x(g,e.get(a),3);case 3:return f=g.g,f.status="QUEUED",x(g,X(e.f.put(f,void 0)),4);case 4:return g["return"](f)}})})}
function Jf(a){return M(this,function c(){var d,e,f;return z(c,function(g){switch(g.f){case 1:return x(g,Ef(),2);case 2:return d=g.g,e=d.A(["LogsRequestsStore"],"readwrite").f("LogsRequestsStore"),x(g,e.get(a),3);case 3:return f=g.g,f.status="NEW",f.S+=1,x(g,X(e.f.put(f,void 0)),4);case 4:return g["return"](f)}})})}
function Kf(){return M(this,function b(){var c,d;return z(b,function(e){if(1==e.f)return x(e,Ef(),2);if(3!=e.f)return c=e.g,x(e,c.count("LogsRequestsStore"),3);d=e.g;return e["return"](!d)})})}
function Lf(a){return M(this,function c(){var d;return z(c,function(e){if(1==e.f)return x(e,Ef(),2);d=e.g;return e["return"](d["delete"]("LogsRequestsStore",a))})})}
function Gf(){return M(this,function b(){var c;return z(b,function(d){if(1==d.f){gf.f||(gf.f=new gf);var e={};var f=lc([]);f&&(e.Authorization=f,e["X-Goog-AuthUser"]=Q("SESSION_INDEX",0),"INNERTUBE_HOST_OVERRIDE"in P||(e["X-Origin"]=window.location.origin),U("pageid_as_header_web")&&"DELEGATED_SESSION_ID"in P&&(e["X-Goog-PageId"]=Q("DELEGATED_SESSION_ID")));e=Tc(e);return x(d,e,2)}c=d.g;return d["return"]($e(c))})})}
;var Mf=ae("network_polling_interval",3E4);function Nf(){this.i=0;this.f=window.navigator.onLine;Of(this);Pf(this)}
function Qf(){Nf.f||(Nf.f=new Nf);return Nf.f}
function Rf(a){var b=Sf,c=Tf;a.i||Uf(a);(new N(function(d){a.h=d})).then(function(){b();
c&&(a.g=c)})}
function Pf(a){window.addEventListener("online",function(){a.f=!0;a.h&&a.h()})}
function Of(a){window.addEventListener("offline",function(){a.f=!1;a.g&&a.g()})}
function Uf(a){a.i=ce(function(){window.navigator.onLine?(!1===a.f&&Ad(Error("NetworkStatusManager missed online event.")),a.f=!0,a.h&&a.h()):(!0===a.f&&Ad(Error("NetworkStatusManager missed offline event.")),a.f=!1,a.g&&a.g());Uf(a)},Mf)}
;var Vf=ae("networkless_throttle_timeout")||100,Wf=ae("networkless_retry_attempts")||1,Xf=0;function Yf(a,b){Cf().then(function(c){if(c&&!U("networkless_bypass_write")){var d={url:a,options:b,timestamp:W(),status:"NEW",S:0};Ff(d).then(function(e){d.id=e;e=Qf();e.f?Zf(d):Rf(e)})["catch"](function(){Zf(d);
Ad(Error("Networkless Logging: Log request setting to indexedDB failed."))})}else Qe(a,b)})}
function Sf(){Xf||(Xf=de(function(){Zf();Xf=0;Sf()},1,Vf))}
function Tf(){var a=Xf;if(!isNaN(a)){var b=C("yt.scheduler.instance.cancelJob");b?b(a):window.clearTimeout(a)}Xf=0}
function Zf(a){M(this,function c(){var d=this,e,f,g,k;return z(c,function(h){switch(h.f){case 1:e=d;if(!a)return x(h,Hf(),6);if(!a.id){h.v(3);break}return x(h,If(a.id),5);case 5:a=h.g;h.v(3);break;case 6:if(a=h.g){h.v(3);break}return x(h,Kf(),8);case 8:return(f=h.g)&&Tf(),h["return"]();case 3:if($f(a))g=a.options.onError?a.options.onError:function(){},k=a.options.onSuccess?a.options.onSuccess:function(){},a.options.onError=function(l,m){return M(e,function r(){return z(r,function(p){if(1==p.f)return a&&
a.id?a.S<Wf?x(p,Jf(a.id),6):x(p,Lf(a.id),2):p.v(2);
2!=p.f&&(Xf||Rf(Qf()),g(l,m));g(l,m);p.f=0})})},a.options.onSuccess=function(l,m){return M(e,function r(){return z(r,function(p){if(1==p.f)return a&&a.id?x(p,Lf(a.id),2):p.v(2);
k(l,m);p.f=0})})},Qe(a.url,a.options);
else if(Bd(Error("Networkless Logging: Stored logs request expired age limit")),a.id)return x(h,Lf(a.id),0);h.v(0)}})})}
function $f(a){a=a.timestamp;return 2592E6<=W()-a?!1:!0}
;function ag(a,b){for(var c=[],d=1;d<arguments.length;++d)c[d-1]=arguments[d];d=Error.call(this,a);this.message=d.message;"stack"in d&&(this.stack=d.stack);this.args=[].concat(c instanceof Array?c:fa(u(c)))}
w(ag,Error);function bg(a){var b=this;this.f=null;a?this.f=a:Xe()&&(this.f=we());ce(function(){ff(b)},5E3)}
bg.prototype.isReady=function(){!this.f&&Xe()&&(this.f=we());return!!this.f};
function ze(a,b,c,d){!Q("VISITOR_DATA")&&"visitor_id"!==b&&.01>Math.random()&&Bd(new ag("Missing VISITOR_DATA when sending innertube request.",b,c,d));if(!a.isReady())throw b=new ag("innertube xhrclient not ready",b,c,d),Ad(b),b.f=0,b;var e={headers:{"Content-Type":"application/json"},method:"POST",u:c,ca:"JSON",I:function(){d.I()},
aa:d.I,onSuccess:function(p,v){if(d.onSuccess)d.onSuccess(v)},
Z:function(p){if(d.onSuccess)d.onSuccess(p)},
onError:function(p,v){if(d.onError)d.onError(v)},
La:function(p){if(d.onError)d.onError(p)},
timeout:d.timeout,withCredentials:!0},f="",g=a.f.ma;g&&(f=g);g=a.f.oa||!1;var k=Ye(g,f,d);Object.assign(e.headers,k);e.headers.Authorization&&!f&&(e.headers["x-origin"]=window.location.origin);var h="/youtubei/"+a.f.innertubeApiVersion+"/"+b,l={alt:"json"};a.f.na&&e.headers.Authorization||(l.key=a.f.innertubeApiKey);h=Od(""+f+h,l||{},!0);var m;if(d.retry&&U("retry_web_logging_batches")&&"www.youtube-nocookie.com"!=f&&(m=df(b,c,k,g))){var n=e.onSuccess,r=e.Z;e.onSuccess=function(p,v){ef(m);n(p,v)};
c.Z=function(p,v){ef(m);r(p,v)}}try{U("use_fetch_for_op_xhr")?Ne(h,e):U("networkless_logging")&&d.retry?(e.method="POST",Yf(h,e)):(e.method="POST",e.u||(e.u={}),Qe(h,e))}catch(p){if("InvalidAccessError"==p.name)m&&(ef(m),m=0),Bd(Error("An extension is blocking network request."));
else throw p;}m&&ce(function(){ff(a)},5E3)}
;var cg=[{X:function(a){return"Cannot read property '"+a.key+"'"},
P:{TypeError:[{regexp:/Cannot read property '([^']+)' of (null|undefined)/,groups:["key","value"]},{regexp:/\u65e0\u6cd5\u83b7\u53d6\u672a\u5b9a\u4e49\u6216 (null|undefined) \u5f15\u7528\u7684\u5c5e\u6027\u201c([^\u201d]+)\u201d/,groups:["value","key"]},{regexp:/\uc815\uc758\ub418\uc9c0 \uc54a\uc74c \ub610\ub294 (null|undefined) \ucc38\uc870\uc778 '([^']+)' \uc18d\uc131\uc744 \uac00\uc838\uc62c \uc218 \uc5c6\uc2b5\ub2c8\ub2e4./,groups:["value","key"]},{regexp:/No se puede obtener la propiedad '([^']+)' de referencia nula o sin definir/,
groups:["key"]},{regexp:/Unable to get property '([^']+)' of (undefined or null) reference/,groups:["key","value"]}],Error:[{regexp:/(Permission denied) to access property "([^']+)"/,groups:["reason","key"]}]}},{X:function(a){return"Cannot call '"+a.key+"'"},
P:{TypeError:[{regexp:/(?:([^ ]+)?\.)?([^ ]+) is not a function/,groups:["base","key"]},{regexp:/Object (.*) has no method '([^ ]+)'/,groups:["base","key"]},{regexp:/Object doesn't support property or method '([^ ]+)'/,groups:["key"]},{regexp:/\u30aa\u30d6\u30b8\u30a7\u30af\u30c8\u306f '([^']+)' \u30d7\u30ed\u30d1\u30c6\u30a3\u307e\u305f\u306f\u30e1\u30bd\u30c3\u30c9\u3092\u30b5\u30dd\u30fc\u30c8\u3057\u3066\u3044\u307e\u305b\u3093/,groups:["key"]},{regexp:/\uac1c\uccb4\uac00 '([^']+)' \uc18d\uc131\uc774\ub098 \uba54\uc11c\ub4dc\ub97c \uc9c0\uc6d0\ud558\uc9c0 \uc54a\uc2b5\ub2c8\ub2e4./,
groups:["key"]}]}}];var dg=new Set,eg=0;function fg(a,b,c,d){c+="."+a;a=String(JSON.stringify(b)).substr(0,500);d[c]=a;return c.length+a.length}
;function Y(a,b,c){this.l=this.f=this.g=null;this.j=Ia(this);this.h=0;this.s=!1;this.m=[];this.i=null;this.B=c;this.G={};c=document;if(a="string"===typeof a?c.getElementById(a):a)if(c="iframe"==a.tagName.toLowerCase(),b.host||(b.host=c?Vb(a.src):"https://www.youtube.com"),this.g=new Xd(b),c||(b=gg(this,a),this.l=a,(c=a.parentNode)&&c.replaceChild(b,a),a=b),this.f=a,this.f.id||(this.f.id="widget"+Ia(this.f)),Rd[this.f.id]=this,window.postMessage){this.i=new O;hg(this);b=T(this.g,"events");for(var d in b)b.hasOwnProperty(d)&&
this.addEventListener(d,b[d]);for(var e in Td)ig(this,e)}}
q=Y.prototype;q.setSize=function(a,b){this.f.width=a;this.f.height=b;return this};
q.pa=function(){return this.f};
q.da=function(a){this.J(a.event,a)};
q.addEventListener=function(a,b){var c=b;"string"==typeof b&&(c=function(){window[b].apply(window,arguments)});
if(!c)return this;this.i.subscribe(a,c);jg(this,a);return this};
function ig(a,b){var c=b.split(".");if(2==c.length){var d=c[1];a.B==c[0]&&jg(a,d)}}
q.destroy=function(){this.f.id&&(Rd[this.f.id]=null);var a=this.i;a&&"function"==typeof a.dispose&&a.dispose();if(this.l){a=this.f;var b=a.parentNode;b&&b.replaceChild(this.l,a)}else(a=this.f)&&a.parentNode&&a.parentNode.removeChild(a);Zd&&(Zd[this.j]=null);this.g=null;a=this.f;for(var c in Za)Za[c][0]==a&&Hd(c);this.l=this.f=null};
q.L=function(){return{}};
function kg(a,b,c){c=c||[];c=Array.prototype.slice.call(c);b={event:"command",func:b,args:c};a.s?a.T(b):a.m.push(b)}
q.J=function(a,b){if(!this.i.h){var c={target:this,data:b};this.i.R(a,c);Wd(this.B+"."+a,c)}};
function gg(a,b){for(var c=document.createElement("iframe"),d=b.attributes,e=0,f=d.length;e<f;e++){var g=d[e].value;null!=g&&""!=g&&"null"!=g&&c.setAttribute(d[e].name,g)}c.setAttribute("frameBorder",0);c.setAttribute("allowfullscreen",1);c.setAttribute("allow","accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture");c.setAttribute("title","YouTube "+T(a.g,"title"));(d=T(a.g,"width"))&&c.setAttribute("width",d);(d=T(a.g,"height"))&&c.setAttribute("height",d);var k=a.L();k.enablejsapi=
window.postMessage?1:0;window.location.host&&(k.origin=window.location.protocol+"//"+window.location.host);k.widgetid=a.j;window.location.href&&I(["debugjs","debugcss"],function(h){var l=window.location.href;var m=l.search(Yb);b:{var n=0;for(var r=h.length;0<=(n=l.indexOf(h,n))&&n<m;){var p=l.charCodeAt(n-1);if(38==p||63==p)if(p=l.charCodeAt(n+r),!p||61==p||38==p||35==p)break b;n+=r+1}n=-1}if(0>n)l=null;else{r=l.indexOf("&",n);if(0>r||r>m)r=m;n+=h.length+1;l=decodeURIComponent(l.substr(n,r-n).replace(/\+/g,
" "))}null!==l&&(k[h]=l)});
c.src=T(a.g,"host")+a.M()+"?"+Xb(k);return c}
q.ba=function(){this.f&&this.f.contentWindow?this.T({event:"listening"}):window.clearInterval(this.h)};
function hg(a){Yd(a.g,a,a.j);a.h=Ld(D(a.ba,a));Jd(a.f,"load",D(function(){window.clearInterval(this.h);this.h=Ld(D(this.ba,this))},a))}
function jg(a,b){a.G[b]||(a.G[b]=!0,kg(a,"addEventListener",[b]))}
q.T=function(a){a.id=this.j;a.channel="widget";a=Oc(a);var b=this.g;var c=Vb(this.f.src||"");b=0==c.indexOf("https:")?[c]:b.f?[c.replace("http:","https:")]:b.h?[c]:[c,c.replace("http:","https:")];if(this.f.contentWindow)for(c=0;c<b.length;c++)try{this.f.contentWindow.postMessage(a,b[c])}catch(S){if(S.name&&"SyntaxError"==S.name){if(!(S.message&&0<S.message.indexOf("target origin ''"))){var d=void 0,e=void 0,f=S;e=void 0===e?{}:e;e.name=Q("INNERTUBE_CONTEXT_CLIENT_NAME",1);e.version=Q("INNERTUBE_CONTEXT_CLIENT_VERSION",
void 0);var g=e||{};e="WARNING";e=void 0===e?"ERROR":e;d=void 0===d?!1:d;if(f){if(U("console_log_js_exceptions")){var k=f,h=[];h.push("Name: "+k.name);h.push("Message: "+k.message);k.hasOwnProperty("params")&&h.push("Error Params: "+JSON.stringify(k.params));h.push("File name: "+k.fileName);h.push("Stacktrace: "+k.stack);window.console.log(h.join("\n"),k)}if((window&&window.yterr||d)&&!(5<=eg)&&0!==f.f){var l=void 0,m=Lb(f);d=m.message||"Unknown Error";k=m.name||"UnknownError";h=m.lineNumber||"Not available";
var n=m.fileName||"Not available";m=m.stack||f.g||"Not available";if(f.hasOwnProperty("args")&&f.args&&f.args.length){var r=0;for(l=0;l<f.args.length;l++){var p=f.args[l],v="params."+l;r+=v.length;if(p)if(Array.isArray(p))for(var y=g,F=0;F<p.length&&!(p[F]&&(r+=fg(F,p[F],v,y),500<r));F++);else if("object"===typeof p)for(y in y=void 0,F=g,p){if(p[y]&&(r+=fg(y,p[y],v,F),500<r))break}else g[v]=String(JSON.stringify(p)).substring(0,500),r+=g[v].length;else g[v]=String(JSON.stringify(p)).substring(0,500),
r+=g[v].length;if(500<=r)break}}else if(f.hasOwnProperty("params")&&f.params)if(p=f.params,"object"===typeof f.params)for(l in v=0,p){if(p[l]&&(r="params."+l,y=String(JSON.stringify(p[l])).substr(0,500),g[r]=y,v+=r.length+y.length,500<v))break}else g.params=String(JSON.stringify(p)).substr(0,500);g={message:d,name:k,lineNumber:h,fileName:n,stack:m,params:g};f=Number(f.columnNumber);isNaN(f)||(g.lineNumber=g.lineNumber+":"+f);f=g;g=u(cg);for(d=g.next();!d.done;d=g.next())if(d=d.value,d.P[f.name])for(h=
u(d.P[f.name]),k=h.next();!k.done;k=h.next())if(n=k.value,k=f.message.match(n.regexp)){f.params["error.original"]=k[0];h=n.groups;n={};for(m=0;m<h.length;m++)n[h[m]]=k[m+1],f.params["error."+h[m]]=k[m+1];f.message=d.X(n);break}window.yterr&&"function"===typeof window.yterr&&window.yterr(f);if(!(dg.has(f.message)||0<=f.stack.indexOf("/YouTubeCenter.js")||0<=f.stack.indexOf("/mytube.js"))){if(U("kevlar_gel_error_routing")){g=void 0;k=e;n=f;h={stackTrace:n.stack};n.fileName&&(h.filename=n.fileName);
d=n.lineNumber&&n.lineNumber.split?n.lineNumber.split(":"):[];0!==d.length&&(1!==d.length||isNaN(Number(d[0]))?2!==d.length||isNaN(Number(d[0]))||isNaN(Number(d[1]))||(h.lineNumber=Number(d[0]),h.columnNumber=Number(d[1])):h.lineNumber=Number(d[0]));d={level:"ERROR_LEVEL_UNKNOWN",message:n.message};"ERROR"===k?d.level="ERROR_LEVEL_ERROR":"WARNING"===k&&(d.level="ERROR_LEVEL_WARNNING");k={isObfuscated:!0,browserStackInfo:h};h={pageUrl:window.location.href,kvPairs:[]};if(n=n.params)for(m=u(Object.keys(n)),
l=m.next();!l.done;l=m.next())l=l.value,h.kvPairs.push({key:"client."+l,value:String(n[l])});h={errorMetadata:h,stackTrace:k,logMessage:d};g=void 0===g?{}:g;d=bg;Q("ytLoggingEventsDefaultDisabled",!1)&&bg==bg&&(d=null);g=void 0===g?{}:g;k={};k.eventTimeMs=Math.round(g.timestamp||W());k.clientError=h;h=String;g.timestamp?n=-1:(n=C("_lact",window),null==n?n=-1:n=Math.max(E()-n,0));k.context={lastActivityMs:h(n)};U("log_sequence_info_on_gel_web")&&g.ea&&(h=k.context,n=g.ea,Ae[n]=n in Ae?Ae[n]+1:0,h.sequence=
{index:Ae[n],groupKey:n},g.Ia&&delete Ae[g.ea]);g=g.Ha;h="";g&&(h=g,n={},h.videoId?n.videoId=h.videoId:h.playlistId&&(n.playlistId=h.playlistId),re[g.token]=n,h=g.token);g=qe.get(h)||[];qe.set(h,g);g.push(k);d&&(ke=new d);d=ae("web_logging_max_batch")||100;k=W();g.length>=d?se():10<=k-ne&&(ue(),ne=k);se()}d=f;g=d.params||{};e={qa:{a:"logerror",t:"jserror",type:d.name,msg:d.message.substr(0,250),line:d.lineNumber,level:e,"client.name":g.name},u:{url:Q("PAGE_NAME",window.location.href),file:d.fileName},
method:"POST"};g.version&&(e["client.version"]=g.version);if(e.u){d.stack&&(e.u.stack=d.stack);d=u(Object.keys(g));for(k=d.next();!k.done;k=d.next())k=k.value,e.u["client."+k]=g[k];if(g=Q("LATEST_ECATCHER_SERVICE_TRACKING_PARAMS",void 0))for(d=u(Object.keys(g)),k=d.next();!k.done;k=d.next())k=k.value,e.u[k]=g[k];g=Q("SERVER_NAME",void 0);d=Q("SERVER_VERSION",void 0);g&&d&&(e.u["server.name"]=g,e.u["server.version"]=d)}Qe(Q("ECATCHER_REPORT_HOST","")+"/error_204",e);dg.add(f.message);eg++}}}}}else throw S;
}else console&&console.warn&&console.warn("The YouTube player is not attached to the DOM. API calls should be made after the onReady event. See more: https://developers.google.com/youtube/iframe_api_reference#Events")};function lg(a){return(0===a.search("cue")||0===a.search("load"))&&"loadModule"!==a}
function mg(a){return 0===a.search("get")||0===a.search("is")}
;function Z(a,b){if(!a)throw Error("YouTube player element ID required.");var c={title:"video player",videoId:"",width:640,height:360};if(b)for(var d in b)c[d]=b[d];Y.call(this,a,c,"player");this.D={};this.playerInfo={}}
w(Z,Y);q=Z.prototype;q.M=function(){return"/embed/"+T(this.g,"videoId")};
q.L=function(){var a=T(this.g,"playerVars");if(a){var b={},c;for(c in a)b[c]=a[c];a=b}else a={};window!=window.top&&document.referrer&&(a.widget_referrer=document.referrer.substring(0,256));if(c=T(this.g,"embedConfig")){if(Ha(c))try{c=JSON.stringify(c)}catch(d){console.error("Invalid embed config JSON",d)}a.embed_config=c}return a};
q.da=function(a){var b=a.event;a=a.info;switch(b){case "apiInfoDelivery":if(Ha(a))for(var c in a)this.D[c]=a[c];break;case "infoDelivery":ng(this,a);break;case "initialDelivery":window.clearInterval(this.h);this.playerInfo={};this.D={};og(this,a.apiInterface);ng(this,a);break;default:this.J(b,a)}};
function ng(a,b){if(Ha(b))for(var c in b)a.playerInfo[c]=b[c]}
function og(a,b){I(b,function(c){this[c]||("getCurrentTime"==c?this[c]=function(){var d=this.playerInfo.currentTime;if(1==this.playerInfo.playerState){var e=(E()/1E3-this.playerInfo.currentTimeLastUpdated_)*this.playerInfo.playbackRate;0<e&&(d+=Math.min(e,1))}return d}:lg(c)?this[c]=function(){this.playerInfo={};
this.D={};kg(this,c,arguments);return this}:mg(c)?this[c]=function(){var d=0;
0===c.search("get")?d=3:0===c.search("is")&&(d=2);return this.playerInfo[c.charAt(d).toLowerCase()+c.substr(d+1)]}:this[c]=function(){kg(this,c,arguments);
return this})},a)}
q.getVideoEmbedCode=function(){var a=parseInt(T(this.g,"width"),10),b=parseInt(T(this.g,"height"),10),c=T(this.g,"host")+this.M();qb.test(c)&&(-1!=c.indexOf("&")&&(c=c.replace(kb,"&amp;")),-1!=c.indexOf("<")&&(c=c.replace(lb,"&lt;")),-1!=c.indexOf(">")&&(c=c.replace(mb,"&gt;")),-1!=c.indexOf('"')&&(c=c.replace(nb,"&quot;")),-1!=c.indexOf("'")&&(c=c.replace(ob,"&#39;")),-1!=c.indexOf("\x00")&&(c=c.replace(pb,"&#0;")));return'<iframe width="'+a+'" height="'+b+'" src="'+c+'" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>'};
q.getOptions=function(a){return this.D.namespaces?a?this.D[a].options||[]:this.D.namespaces||[]:[]};
q.getOption=function(a,b){if(this.D.namespaces&&a&&b)return this.D[a][b]};
function pg(a){if("iframe"!=a.tagName.toLowerCase()){var b=R(a,"videoid");b&&(b={videoId:b,width:R(a,"width"),height:R(a,"height")},new Z(a,b))}}
;function qg(a,b){var c={title:"Thumbnail",videoId:"",width:120,height:68};if(b)for(var d in b)c[d]=b[d];Y.call(this,a,c,"thumbnail")}
w(qg,Y);qg.prototype.M=function(){return"/embed/"+T(this.g,"videoId")};
qg.prototype.L=function(){return{player:0,thumb_width:T(this.g,"thumbWidth"),thumb_height:T(this.g,"thumbHeight"),thumb_align:T(this.g,"thumbAlign")}};
qg.prototype.J=function(a,b){Y.prototype.J.call(this,a,b?b.info:void 0)};
function rg(a){if("iframe"!=a.tagName.toLowerCase()){var b=R(a,"videoid");if(b){b={videoId:b,events:{},width:R(a,"width"),height:R(a,"height"),thumbWidth:R(a,"thumb-width"),thumbHeight:R(a,"thumb-height"),thumbAlign:R(a,"thumb-align")};var c=R(a,"onclick");c&&(b.events.onClick=c);new qg(a,b)}}}
;G("YT.PlayerState.UNSTARTED",-1);G("YT.PlayerState.ENDED",0);G("YT.PlayerState.PLAYING",1);G("YT.PlayerState.PAUSED",2);G("YT.PlayerState.BUFFERING",3);G("YT.PlayerState.CUED",5);G("YT.get",function(a){return Rd[a]});
G("YT.scan",Ud);G("YT.subscribe",function(a,b,c){fd.subscribe(a,b,c);Td[a]=!0;for(var d in Rd)ig(Rd[d],a)});
G("YT.unsubscribe",function(a,b,c){ed(a,b,c)});
G("YT.Player",Z);G("YT.Thumbnail",qg);Y.prototype.destroy=Y.prototype.destroy;Y.prototype.setSize=Y.prototype.setSize;Y.prototype.getIframe=Y.prototype.pa;Y.prototype.addEventListener=Y.prototype.addEventListener;Z.prototype.getVideoEmbedCode=Z.prototype.getVideoEmbedCode;Z.prototype.getOptions=Z.prototype.getOptions;Z.prototype.getOption=Z.prototype.getOption;Sd.push(function(a){a=Vd("player",a);I(a,pg)});
Sd.push(function(){var a=Vd("thumbnail");I(a,rg)});
"undefined"!=typeof YTConfig&&YTConfig.parsetags&&"onload"!=YTConfig.parsetags||Ud();var sg=B.onYTReady;sg&&sg();var tg=B.onYouTubeIframeAPIReady;tg&&tg();var ug=B.onYouTubePlayerAPIReady;ug&&ug();}).call(this);
