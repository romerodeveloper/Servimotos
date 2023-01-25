$(function () {

    $("input[name='tasaGanacia']").TouchSpin({
        min: 0,
        max: 100,
        step: 1,
        decimals: 2,
        boostat: 5,
        maxboostedstep: 10,
        postfix: '%'
    }).on('change', function () {
        calculate();
    })
    .val($("input[name='tasaGanacia']").val())


    // evento de cantidad
    $('.form-group')
        .on('change', 'input[name="precioCosto"]', function () {
            calculate()
        });

    $('.form-group')
        .on('change', 'input[name="nombre"]', function () {
            var cont = $('input[name="nombre"]').val()
            $('input[name="nombre"]').val(cont.toUpperCase())
        });

});

function calculate(){
    var precio = $('input[name="precioCosto"]').val();
    var tasa = $('input[name="tasaGanacia"]').val();
    var iva = parseFloat(precio)*19/100;
    var total = parseFloat(precio) + iva
    var precioCal = total + total*(parseFloat(tasa)/100)
    $('input[name="precioFinal"]').val(Math.round(precioCal));
    $('input[name="iva"]').val(iva);
}
