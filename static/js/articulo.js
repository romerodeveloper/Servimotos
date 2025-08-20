var precioCostoReal = 0.0;
var estadoIva = '';
var initialFormValues = {};

$(document).ready(function () {

    // Ocultar el contenedor del campo descuentoAntesDeIva y su TouchSpin inicialmente
    $(".descuento-container").hide();

    // Inicializar TouchSpin para descuentoAntesDeIva (pero oculto)
    $("input[name='descuentoAntesDeIva']").TouchSpin({
        min: 0,
        max: 100,
        step: 1,
        decimals: 0,
        boostat: 5,
        maxboostedstep: 10,
        postfix: '%'
    }).on('change', function () {
        calcularPrecios();
    });

    // Inicializar TouchSpin para tasaGanacia
    $("input[name='tasaGanacia']").TouchSpin({
        min: 0,
        max: 100,
        step: 1,
        decimals: 0,
        boostat: 5,
        maxboostedstep: 10,
        postfix: '%'
    }).on('change', function () {
        calcularPrecios();
    });

    // Calcular al cambiar el precioCosto
    $('input[name="precioCosto"]').on('change', function () {
        calcularPrecios();
    });

    // Convertir el nombre a mayúsculas
    $('input[name="nombre"]').on('change', function () {
        $(this).val($(this).val().toUpperCase());
    });

    // Verificar el modelo de factura al cambiar el select de distribuidor
    $("select[name='distribuidor']").on('change', function () {
        verificarModeloFactura();
        //actualizarLabelDisctribuidor();
    });

    verificarModeloFactura();
    if ($('input[name="action"]').val() == 'edit'){
        procesarFormularioDeEdicion()
    }


    $('form').on('submit', function (e) {
        e.preventDefault();

        var articulo = {
            nombre: $('input[name="nombre"]').val(),
            codigoOriginal: $('input[name="codigoOriginal"]').val(),
            distribuidor: $('select[name="distribuidor"]').val(),
            descuentoAntesDeIva: $('input[name="descuentoAntesDeIva"]').val(),
            precioCosto: precioCostoReal,
            tasaGanacia: $('input[name="tasaGanacia"]').val(),
            iva: $('input[name="iva"]').val(),
            precioFinal: $('input[name="precioFinal"]').val(),
            stock: $('input[name="stock"]').val(),
            categoria: $('select[name="categoria"]').val(),
            marca:  $('select[name="marca"]').val()
        };

        console.log(articulo)

        // Enviar los datos mediante AJAX
        $.ajax({
            url: window.location.pathname,  // URL de la acción add
            method: 'POST',
            data: {
                'action': $('input[name="action"]').val(),
                'articulo': JSON.stringify(articulo)
            },
            success: function (response) {
                if (response.success) {
                    window.location.href = '/articulo/list/';  // Redirigir a la lista
                } else {
                    console.error("Error al guardar el artículo:", response.error);
                }
            },
            error: function (xhr, status, error) {
                console.error("Error en la solicitud AJAX:", error);
            }
        });
    });
});

function verificarModeloFactura() {
    var distribuidorId = $("select[name='distribuidor']").val();
    if (!distribuidorId) return;

    $.ajax({
        url: window.location.pathname,
        method: 'POST',
        data: {
            action: 'search',
            distribuidor: distribuidorId,
        },
        success: function (response) {
            estadoIva = response.modeloFactura;
            console.log(estadoIva);

            actualizarLabelDistribuidor(estadoIva);
            toggleDescuentoContainer(estadoIva === 'No Calculado');
            calcularPrecios();
        },
        error: function (xhr, status, error) {
            console.error("Error en la solicitud AJAX:", error);
        }
    });
}


function actualizarLabelDistribuidor(estadoIva) {
    var label = $("label[for='" + $('select[name="distribuidor"]').attr('id') + "']");
    label.text(`Distribuidor (Configuracion de Iva: ${estadoIva})`);
}

function toggleDescuentoContainer(mostrar) {
    $(".descuento-container").toggle(mostrar);
}

function actualizarLabelPrecioCosto() {
    var label = $("label[for='" + $('input[name="precioCosto"]').attr('id') + "']");
    if (estadoIva === 'Calculado') {
        label.html("Precio distribuidor (Precio Real Sin Iva: " + precioCostoReal + ")");
    } else {
        label.html("Precio distribuidor");
    }
}

function calcularPrecios() {
    if (estadoIva === 'Calculado') {
        calculateWithIVA();
    } else if (estadoIva === 'No Calculado') {
        calculate();
    } else {
        alert('Debe elegir un distribudior primero')
    }
}

function calculate() {
    actualizarLabelPrecioCosto();
    var precioSinIva = parseFloat($('input[name="precioCosto"]').val()) || 0;
    var descuentoPorcentual = parseFloat($('input[name="descuentoAntesDeIva"]').val()) || 0;
    var ganancia = parseFloat($('input[name="tasaGanacia"]').val()) || 0;
    var descuentoNeto = precioSinIva * descuentoPorcentual / 100;
    var iva = (precioSinIva - descuentoNeto) * 19 / 100;
    var total = precioSinIva - descuentoNeto + iva;
    var precioFinal = total + (total * ganancia / 100);
    precioCostoReal = Math.round(precioSinIva - descuentoNeto);

    $('input[name="precioFinal"]').val(Math.round(precioFinal));
    $('input[name="iva"]').val(Math.round(iva));

}

function calculateWithIVA() {
    var precioFinal = parseFloat($('input[name="precioCosto"]').val()) || 0;
    var iva = precioFinal * 19 / 119;
    var precioCostoRealSinIva = precioFinal - iva;
    var tasa = parseFloat($('input[name="tasaGanacia"]').val()) || 0;
    var precioFinalConGanancia = precioFinal + (precioFinal * (tasa / 100));
    precioCostoReal = Math.round(precioCostoRealSinIva);

    actualizarLabelPrecioCosto();
    $('input[name="iva"]').val(Math.round(iva));
    $('input[name="precioFinal"]').val(Math.round(precioFinalConGanancia));
}

async function procesarFormularioDeEdicion() {
    // Primero obtenemos los valores del formulario
    $('form').find('input, select, textarea').each(function() {
        if ($(this).attr('name') != 'action' && $(this).attr('name') != 'csrfmiddlewaretoken') {
            initialFormValues[$(this).attr('name')] = $(this).val();
        }
    });

    // Verificamos el estadoIva antes de realizar los cálculos
    var costo = parseInt(initialFormValues.precioCosto) || 0;
    var iva = parseInt(initialFormValues.iva) || 0;
    var descuentoPorcentual = parseInt(initialFormValues.descuentoAntesDeIva) || 0;
    var descuento = costo * descuentoPorcentual / (100 + descuentoPorcentual);

    // Verificamos el estadoIva, ahora con async/await
    var estado = await verificarEstadoFacturaEdit(initialFormValues.distribuidor);
    console.log(estadoIva, "en edit");

    if (estado === 'Calculado') {
        $('input[name="precioCosto"]').val(Math.round(costo + iva));
        calculateWithIVA();
    } else {
        $('input[name="precioCosto"]').val(Math.round(costo + descuento));
        calculate();
    }

    console.log(initialFormValues);
}

// Función corregida para devolver una promesa y manejar la asincronía
function verificarEstadoFacturaEdit(distribuidorId) {
    return new Promise(function(resolve, reject) {
        if (!distribuidorId) {
            resolve(null);  // Si no hay distribuidorId, no procedemos
            return;
        }

        $.ajax({
            url: window.location.pathname,
            method: 'POST',
            data: {
                action: 'search',
                distribuidor: distribuidorId,
            },
            success: function(response) {
                var respuesta = response.modeloFactura;
                resolve(respuesta);  // Devolvemos la respuesta al resolver la promesa
            },
            error: function(xhr, status, error) {
                console.error("Error en la solicitud AJAX:", error);
                reject(error);  // Rechazamos la promesa en caso de error
            }
        });
    });
}
