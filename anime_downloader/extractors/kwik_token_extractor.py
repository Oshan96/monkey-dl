from js2py.pyjs import *

# setting scope
var = Scope(JS_BUILTINS)
set_global_object(var)

# Code follows:
var.registers(['extract_data', '_0xe12c'])


@Js
def PyJsHoisted__0xe12c_(d, e, f, this, arguments, var=var):
    var = Scope({'d': d, 'e': e, 'f': f, 'this': this, 'arguments': arguments}, var)
    var.registers(['e', 'i', 'h', 'g', 'k', 'd', 'j', 'f'])
    var.put('g', Js('0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ+/').callprop('split', Js('')))
    var.put('h', var.get('g').callprop('slice', Js(0.0), var.get('e')))
    var.put('i', var.get('g').callprop('slice', Js(0.0), var.get('f')))

    @Js
    def PyJs_anonymous_0_(a, b, c, this, arguments, var=var):
        var = Scope({'a': a, 'b': b, 'c': c, 'this': this, 'arguments': arguments}, var)
        var.registers(['b', 'c', 'a'])
        if PyJsStrictNeq(var.get('h').callprop('indexOf', var.get('b')), (-Js(1.0))):
            return var.put('a', (
                        var.get('h').callprop('indexOf', var.get('b')) * var.get('Math').callprop('pow', var.get('e'),
                                                                                                  var.get('c'))), '+')

    PyJs_anonymous_0_._set_name('anonymous')
    var.put('j',
            var.get('d').callprop('split', Js('')).callprop('reverse').callprop('reduce', PyJs_anonymous_0_, Js(0.0)))
    var.put('k', Js(''))
    while (var.get('j') > Js(0.0)):
        var.put('k', (var.get('i').get((var.get('j') % var.get('f'))) + var.get('k')))
        var.put('j', ((var.get('j') - (var.get('j') % var.get('f'))) / var.get('f')))
    return (var.get('k') or Js('0'))


PyJsHoisted__0xe12c_.func_name = '_0xe12c'
var.put('_0xe12c', PyJsHoisted__0xe12c_)


@Js
def PyJsHoisted_extract_data_(h, u, n, t, e, r, this, arguments, var=var):
    var = Scope({'h': h, 'u': u, 'n': n, 't': t, 'e': e, 'r': r, 'this': this, 'arguments': arguments}, var)
    var.registers(['e', 'len', 'i', 'h', 'u', 'n', 'r', 's', 't', 'j'])
    var.put('r', Js(''))
    # for JS loop
    var.put('i', Js(0.0))
    var.put('len', var.get('h').get('length'))
    while (var.get('i') < var.get('len')):
        try:
            var.put('s', Js(''))
            while PyJsStrictNeq(var.get('h').get(var.get('i')), var.get('n').get(var.get('e'))):
                var.put('s', var.get('h').get(var.get('i')), '+')
                (var.put('i', Js(var.get('i').to_number()) + Js(1)) - Js(1))
            # for JS loop
            var.put('j', Js(0.0))
            while (var.get('j') < var.get('n').get('length')):
                try:
                    var.put('s', var.get('s').callprop('replace',
                                                       var.get('RegExp').create(var.get('n').get(var.get('j')),
                                                                                Js('g')), var.get('j')))
                finally:
                    (var.put('j', Js(var.get('j').to_number()) + Js(1)) - Js(1))
            var.put('r', var.get('String').callprop('fromCharCode', (
                        var.get('_0xe12c')(var.get('s'), var.get('e'), Js(10.0)) - var.get('t'))), '+')
        finally:
            (var.put('i', Js(var.get('i').to_number()) + Js(1)) - Js(1))
    return var.get('decodeURIComponent')(var.get('escape')(var.get('r')))


PyJsHoisted_extract_data_.func_name = 'extract_data'
var.put('extract_data', PyJsHoisted_extract_data_)

kwik_token_extractor = var.to_python()
