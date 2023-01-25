
var tblProducts;

var comps = {
    items: {
        distribuidor: '',
        date_joined: '',
        subtotal: parseFloat(0.00),
        iva: parseFloat(0.00),
        total: parseFloat(0.00),
        products: [],
        articulosEliminados: [],
        contador: 0
    },
    calculate_invoice: function () {
        var subtotal = 0.00;
        var iva = $('input[name="iva"]').val();
        $.each(this.items.products, function (pos, dict) {
            console.log(dict)
            var precio = dict.precioCosto;
            var precioIva = precio + (precio*(19/100));
            var precioCal = precioIva + (precioIva*((dict.tasaGanacia)/100));
            dict.ivaProd = precio*(19/100)
            dict.precioFinal = precioCal
            dict.subtotal = dict.cant * parseFloat(dict.precioCosto);
            subtotal+=dict.subtotal;
        });
        this.items.subtotal = subtotal;
        this.items.iva = subtotal * (iva/100);
        this.items.total = this.items.subtotal + this.items.iva;

        $('input[name="subtotal"]').val(this.items.subtotal.toFixed(2));
        $('input[name="ivacalc"]').val(this.items.iva.toFixed(2));
        $('input[name="total"]').val(this.items.total.toFixed(2));
    },
    llenar: function () {
        this.items.contador = 1;
        $.each(this.items.products, function (pos, dict) {
            dict.cantidadIni = dict.cant
        });

    },
    add: function (item) {
        if (this.items.products.length == 0){
            this.items.products.push(item);
        }else{
            repetido = false
            $.each(this.items.products, function (pos, dict) {
                if (dict.id == item.id) {
                    dict.cant += item.cant;
                    repetido = true
                }
            });
            if (repetido == false){
                this.items.products.push(item);
            }
        }
        this.list();
    },
    list: function () {
        if (this.items.contador == 0){
            this.llenar();
        }
        this.calculate_invoice();

        tblProducts = $('#tblProducts').DataTable({
            responsive: true,
            autoWidth: false,
            destroy: true,
            data: this.items.products,
            columns: [
                {"data": "id"},
                {"data": "nombre"},
                {"data": "precioCosto"},
                {"data": "tasaGanacia"},
                {"data": "cant"},
                {"data": "subtotal"},
                {"data": "precioFinal"},
            ],
            columnDefs: [
                {
                    targets: [0],
                    class: 'text-center',
                    orderable: false,
                    render: function (data, type, row) {
                        return '<a rel="remove" class="btn btn-danger btn-xs btn-flat"><i class="fas fa-trash-alt"></i></a>';
                    }
                },
                {
                    targets: [-5],
                    class: 'text-center',
                    orderable: false,
                    render: function (data, type, row) {
                        return '<input type="text" name="precioC" class="form-control form-control-sm input-sm" autocomplete="off" value="' + row.precioCosto + '">';
                    }
                },
                {
                    targets: [-4],
                    class: 'text-center',
                    orderable: false,
                    render: function (data, type, row) {
                        return '<input type="text" name="tasa" class="form-control form-control-sm input-sm" autocomplete="off" value="' + row.tasaGanacia + '">';
                    }
                },
                {
                    targets: [-3],
                    class: 'text-center',
                    orderable: false,
                    render: function (data, type, row) {
                        return '<input type="text" name="cant" class="form-control form-control-sm input-sm" autocomplete="off" value="' + row.cant + '">';
                    }
                },
                {
                    targets: [-2],
                    class: 'text-center',
                    orderable: false,
                    render: function (data, type, row) {
                        return '$' + parseFloat(data).toFixed(2);
                    }
                },
                {
                    targets: [-1],
                    class: 'text-center',
                    orderable: false,
                    render: function (data, type, row) {
                        return '$' + parseFloat(data).toFixed(2);
                    }
                },
            ],

            initComplete: function (settings, json) {

            }
        });
    },
};

function formatRepo(repo) {
    if (repo.loading) {
        return repo.text;
    }

    if (!Number.isInteger(repo.id)) {
        return repo.text;
    }

    var option = $(
        '<div class="wrapper container">' +
        '<div class="row">' +
        '<div class="col-lg-1">' +
        '<img src="' + repo.image + '" class="img-fluid img-thumbnail d-block mx-auto rounded">' +
        '</div>' +
        '<div class="col-lg-11 text-left shadow-sm">' +
        //'<br>' +
        '<p style="margin-bottom: 0;">' +
        '<b>Nombre:</b> ' + repo.nombre + '<br>' +
        '<b>Marca:</b> ' + repo.marca.nombre + '<br>' +
        '<b>Cantidad:</b> ' + repo.stock + '<br>' +
        '<b>Precio Publico:</b> <span class="badge badge-warning">$' + repo.precioFinal + '</span>' +
        '</p>' +
        '</div>' +
        '</div>' +
        '</div>');

    return option;
}


$(function () {
    $('.select2').select2({
        theme: "bootstrap4",
        language: 'es'
    });

    $('#date_joined').datetimepicker({
        format: 'YYYY-MM-DD',
        date: moment().format("YYYY-MM-DD"),
        locale: 'es',
        //minDate: moment().format("YYYY-MM-DD")
    });

    $("input[name='iva']").TouchSpin({
        min: 0,
        max: 100,
        step: 0.01,
        decimals: 2,
        boostat: 5,
        maxboostedstep: 10,
        postfix: '%'
    }).on('change', function () {
        comps.calculate_invoice();
    })
    .val(19.0);

    // search products


    // buscador independiente
    $('.btnSearchProducts').on('click', function () {
        tblSearchProducts = $('#tblSearchProducts').DataTable({
            responsive: true,
            autoWidth: false,
            destroy: true,
            deferRender: true,
            ajax: {
                url: window.location.pathname,
                type: 'POST',
                data: {
                    'action': 'search_products',
                    'term': $('select[name="search"]').val()
                },
                dataSrc: ""
            },
            columns: [
                {"data": "nombre"},
                {"data": "marca.nombre"},
                {"data": "stock"},
                {"data": "precioFinal"},
                {"data": "id"},
            ],
            columnDefs: [

                {
                    targets: [-3],
                    class: 'text-center',
                    render: function (data, type, row) {
                        return '<span class="badge badge-secondary">'+data+'</span>';
                    }
                },
                {
                    targets: [-2],
                    class: 'text-center',
                    orderable: false,
                    render: function (data, type, row) {
                        return '$' + parseFloat(data).toFixed(2);
                    }
                },
                {
                    targets: [-1],
                    class: 'text-center',
                    orderable: false,
                    render: function (data, type, row) {
                        var buttons = '<a rel="add" class="btn btn-success btn-xs btn-flat"><i class="fas fa-plus"></i></a> ';
                        return buttons;
                    }
                },
            ],
            initComplete: function (settings, json) {

            }
        });
        $('#myModalSearchProducts').modal('show');
    });

    $('#tblSearchProducts tbody')
        .on('click', 'a[rel="add"]', function () {
            var tr = tblSearchProducts.cell($(this).closest('td, li')).index();
            var product = tblSearchProducts.row(tr.row).data();
            product.cant = 1;
            product.cantidadIni = 0;
            product.subtotal = 0.00;
            comps.add(product);
        });



    // evento de cantidad
    $('#tblProducts tbody')
        .on('click', 'a[rel="remove"]', function () {
            var tr = tblProducts.cell($(this).closest('td, li')).index();
            alert_action('Notificación', '¿Estas seguro de eliminar el producto de tu detalle?', function () {
                comps.items.articulosEliminados.push(comps.items.products[tr.row]);
                comps.items.products.splice(tr.row, 1);
                comps.list();
            });
        })
        .on('change', 'input[name="cant"]', function () {
            console.clear();
            var cant = parseInt($(this).val());
            var tr = tblProducts.cell($(this).closest('td, li')).index();
            console.log(cant, tr)
            comps.items.products[tr.row].cant = cant;
            comps.calculate_invoice();
            $('td:eq(5)', tblProducts.row(tr.row).node()).html('$' + comps.items.products[tr.row].subtotal.toFixed(2));

        })
        .on('change', 'input[name="tasa"]', function () {
            console.clear();
            var tasa = parseInt($(this).val());
            var tr = tblProducts.cell($(this).closest('td, li')).index();
            comps.items.products[tr.row].tasaGanacia = tasa;
            comps.calculate_invoice();
            var precio = comps.items.products[tr.row].precioCosto;
            var precioIva = precio + (precio*(19/100));
            var precioCal = precioIva + (precioIva*((comps.items.products[tr.row].tasaGanacia)/100));
            $('td:eq(6)', tblProducts.row(tr.row).node()).html('$' + precioCal);
        })
        .on('change', 'input[name="precioC"]', function () {
            console.clear();
            var precioCosto = parseInt($(this).val());
            var tr = tblProducts.cell($(this).closest('td, li')).index();
            comps.items.products[tr.row].precioCosto = precioCosto;
            comps.calculate_invoice();
            $('td:eq(5)', tblProducts.row(tr.row).node()).html('$' + comps.items.products[tr.row].subtotal.toFixed(2));
            $('td:eq(6)', tblProducts.row(tr.row).node()).html('$' + comps.items.products[tr.row].precioFinal );
        });

    $('.cont')
        .on('click','.btnRemoveAllItems', function () {
            if (comps.items.products.length === 0) return false;
            alert_action('Notificación', '¿Estas seguro de eliminar todos los items de tu detalle?', function () {
                $.each(comps.items.products, function (pos, dict) {
                     comps.items.articulosEliminados.push(dict)
                });
                comps.items.products = [];
                comps.list();
            });
    });

    $('.btnClearSearch').on('click', function () {
        $('input[name="search"]').val('').focus();
    });

        // event submit
    $('form').on('submit', function (e) {
        e.preventDefault();

        if(comps.items.products.length === 0){
            message_error('Debe al menos tener un item en su detalle de venta');
            return false;
        }

        comps.items.date_joined = $('input[name="date_joined"]').val();
        comps.items.distribuidor = $('select[name="distribuidor"]').val();
        var parameters = new FormData();
        parameters.append('action', $('input[name="action"]').val());
        parameters.append('comps', JSON.stringify(comps.items));
        submit_with_ajax(window.location.pathname, 'Notificación', '¿Estas seguro de realizar la siguiente acción?', parameters, function () {
            location.href = '/compra/list/';
        });
    });


    $('select[name="search"]').select2({
        theme: "bootstrap4",
        language: 'es',
        allowClear: true,
        ajax: {
            delay: 250,
            type: 'POST',
            url: window.location.pathname,
            data: function (params) {
                var queryParameters = {
                    term: params.term,
                    action: 'search_autocomplete'
                }
                return queryParameters;
            },
            processResults: function (data) {
                return {
                    results: data
                };
            },
        },
        placeholder: 'Ingrese una descripción',
        minimumInputLength: 1,
        templateResult: formatRepo,
    }).on('select2:select', function (e) {
        var data = e.params.data;
        if(!Number.isInteger(data.id)){
            return false;
        }
        data.cant = 1;
        data.subtotal = 0.00;
        data.cantidadIni = 0;
        comps.add(data);
        $(this).val('').trigger('change.select2');
    });

    comps.list();
});