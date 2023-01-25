"""servimotos URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from categorias.views import CategoriaListView, CategoriaCreateView, CategoriaUpdateView, CategoriaDeleteView
from articulos.views import ArticuloListView, ArticuloCreateView, ArticuloUpdateView, ArticuloDeleteView
from login.views import LoginFormView, LogoutView
from ventas.views import VentaCreateView, VentaListView, VentaDeleteView, VentaUpdateView, VentaInvoicePdfView
from marcas.views import MarcaListView, MarcaCreateView, MarcaUpdateView, MarcaDeleteView
from compras.views import CompraCreateView, CompraListView, CompraDeleteView, CompraUpdateView
from reports.views import ReportVentaView
from reports_dos.views import ReportCompraView

from distribuidores.views import DistribuidorListView, DistribuidorCreateView, DistribuidorUpdateView, \
    DistribuidorDeleteView
from webapp.views import IndexView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', IndexView.as_view(), name='index'),
    #URL DE CATEGORIAS
    path('categoria/list/', CategoriaListView.as_view(), name='lista_categoria'),
    path('categoria/add/', CategoriaCreateView.as_view(), name='agregar_categoria' ),
    path('categoria/edit/<int:pk>/', CategoriaUpdateView.as_view(), name='actualizar_categoria' ),
    path('categoria/delete/<int:pk>/', CategoriaDeleteView.as_view(), name='eliminar_categoria' ),
    #URL DE MARCAS
    path('marca/list/', MarcaListView.as_view(), name='lista_marca'),
    path('marca/add/', MarcaCreateView.as_view(), name='agregar_marca' ),
    path('marca/edit/<int:pk>/', MarcaUpdateView.as_view(), name='actualizar_marca' ),
    path('marca/delete/<int:pk>/', MarcaDeleteView.as_view(), name='eliminar_marca' ),
    #URL DE ARTICULOS
    path('articulo/list/', ArticuloListView.as_view(), name='lista_articulo'),
    path('articulo/add/', ArticuloCreateView.as_view(), name='agregar_articulo'),
    path('articulo/edit/<int:pk>/', ArticuloUpdateView.as_view(), name='actualizar_articulo'),
    path('articulo/delete/<int:pk>/', ArticuloDeleteView.as_view(), name='eliminar_articulo'),
    #URL DE DISTRIBUIDORES
    path('distribuidor/list/', DistribuidorListView.as_view(), name='lista_distribuidor'),
    path('distribuidor/add/', DistribuidorCreateView.as_view(), name='agregar_distribuidor'),
    path('distribuidor/edit/<int:pk>/', DistribuidorUpdateView.as_view(), name='actualizar_distribuidor'),
    path('distribuidor/delete/<int:pk>/', DistribuidorDeleteView.as_view(), name='eliminar_distribuidor'),
    #URL DE LOGIN
    path('login/', LoginFormView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    #URL DE VENTA
    path('venta/add/', VentaCreateView.as_view(), name='agregar_venta'),
    path('venta/list/', VentaListView.as_view(), name='lista_venta'),
    path('venta/delete/<int:pk>/', VentaDeleteView.as_view(), name='eliminar_venta'),
    path('venta/edit/<int:pk>/', VentaUpdateView.as_view(), name='actualizar_venta'),
    #URL DE COMPRA
    path('compra/add/', CompraCreateView.as_view(), name='agregar_compra'),
    path('compra/list/', CompraListView.as_view(), name='lista_compra'),
    path('compra/delete/<int:pk>/', CompraDeleteView.as_view(), name='eliminar_compra'),
    path('compra/edit/<int:pk>/', CompraUpdateView.as_view(), name='actualizar_compra'),
    # URL DE REPORTES
    path('reports/venta/', ReportVentaView.as_view(), name='venta_report'),
    path('reports/compra/', ReportCompraView.as_view(), name='compra_report'),
    # URL DE FACTURAS
    path('venta/invoice/pdf/<int:pk>/', VentaInvoicePdfView.as_view(), name='venta_pdf'),

]

