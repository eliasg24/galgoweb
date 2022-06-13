# Django
from django.urls import path
from django.views.generic.base import View

# Views
from dashboards.views import views, views_rest

urlpatterns = [
    path(
        route="",
        view=views.HomeView.as_view(),
        name="home"
    ),
    path(
        route="pulpo/",
        view=views.PulpoView.as_view(),
        name="pulpo"
    ),
    path(
        route="api/",
        view=views.VehiculoAPI.as_view(),
        name="api"
    ),
    path(
        route="api/pro/",
        view=views.PulpoProAPI.as_view(),
        name="apiPro"
    ),
    path(
        route="api/tireeye/",
        view=views.TireEyeAPI.as_view(),
        name="apiTireEye"
    ),
    path(
        route="buscar/",
        view=views.buscar,
        name="buscar"
    ),
    path(
        route="config/",
        view=views.ConfigView.as_view(),
        name="config"
    ),
    path(
        route="search/",
        view=views.SearchView.as_view(),
        name="search"
    ),
    path(
        route="api/vehicle_list/",
        view=views_rest.SearchView.as_view(),
        name="api_search"
    ),
    path(
        route="search_id/",
        view=views.search,
        name="search_id"
    ),
    path(
        route="<int:pk>/",
        view=views.DetailView.as_view(),
        name="detail"
    ),
    path(
        route="estatusDeFlota",
        view=views.TireDBView.as_view(),
        name="tireDB1"
    ),
    path(
        route="reemplazoEstimado",
        view=views.TireDB2View.as_view(),
        name="tireDB2"
    ),
    path(
        route="rendimientoDeLlanta",
        view=views.TireDB3View.as_view(),
        name="tireDB3"
    ),
    path(
        route="dashboardOperativo",
        view=views.dashboardOperativoView.as_view(),
        name="dashboardOperativo"
    ),
    path(
        route="vehiculosformulario",
        view=views.vehiculosformularioView.as_view(),
        name="vehiculosformulario"
    ),
    path(
        route="login/",
        view=views.LoginView.as_view(),
        name="login"
    ),
    path(
        route="logout/",
        view=views.LogoutView.as_view(),
        name="logout"
    ),
    path(
        route="hub",
        view=views.hubView.as_view(),
        name="hub"
    ),
    path(
        route="reporte",
        view=views.ParametroExtractoView.as_view(),
        name="ParametroExtracto"
    ),
    path(
        route="dashboards",
        view=views.SiteMenuView.as_view(),
        name="siteMenu"
    ),
    path(
        route="desechos",
        view=views.catalogoDesechosView.as_view(),
        name="catalogoDesechos"
    ),
    path(
        route="desechos/<int:pk>/",
        view=views.catalogoDesechosEditView.as_view(),
        name="catalogoDesechosEdit"
    ),
    path(
        route="desechos/delete",
        view=views.catalogoDesechosDeleteView,
        name="catalogoDesechosDelete"
    ),
    path(
        route="productos",
        view=views.catalogoProductoView.as_view(),
        name="catalogoProductos"
    ),
    path(
        route="productos/<int:pk>/",
        view=views.catalogoProductoEditView.as_view(),
        name="catalogoProductosEdit"
    ),
    path(
        route="productos/delete",
        view=views.catalogoProductoDeleteView,
        name="catalogoProductoDelete"
    ),
    path(
        route="renovadores",
        view=views.catalogoRenovadoresView.as_view(),
        name="catalogoRenovadores"
    ),
    path(
        route="renovadores/<int:pk>/",
        view=views.catalogoRenovadoresEditView.as_view(),
        name="catalogoRenovadoresEdit"
    ),
    path(
        route="renovadores/delete",
        view=views.catalogoRenovadoresDeleteView,
        name="catalogoRenovadoresDelete"
    ),
    path(
        route="observaciones",
        view=views.catalogoObservacionesView.as_view(),
        name="catalogoObservaciones"
    ),
    path(
        route="observaciones/<int:pk>/",
        view=views.catalogoObservacionesEditView.as_view(),
        name="catalogoObservacionesEdit"
    ),
    path(
        route="observaciones/delete",
        view=views.catalogoObservacionesDeleteView,
        name="catalogoObservacionesDelete"
    ),
    path(
        route="rechazos",
        view=views.catalogoRechazosView.as_view(),
        name="catalogoRechazos"
    ),
    path(
        route="rechazos/<int:pk>/",
        view=views.catalogoRechazosEditView.as_view(),
        name="catalogoRechazosEdit"
    ),
    path(
        route="rechazos/delete",
        view=views.catalogoRechazosDeleteView,
        name="catalogoRechazosDelete"
    ),
    path(
        route="companyFormulario",
        view=views.companyFormularioView.as_view(),
        name="companyFormulario"
    ),
     path(
        route="sucursalFormulario",
        view=views.sucursalFormularioView.as_view(),
        name="sucursalFormulario"
    ),
    path(
        route="sucursalView",
        view=views.sucursalView.as_view(),
        name="sucursalView"
    ),
    path(
        route="aplicacionesView",
        view=views.aplicacionesView.as_view(),
        name="aplicacionesView"
    ),
    path(
        route="vehiculosView",
        view=views.vehiculosView.as_view(),
        name="vehiculosView"
    ),
    path(
        route="llantasView",
        view=views.llantasView.as_view(),
        name="llantasView"
    ),
    path(
        route="inpeccionesView",
        view=views.inpeccionesView.as_view(),
        name="inspeccionesView"
    ),
    path(
        route="inspeccionesAdd/",
        view=views.my_soap_inspeccion(),
        name="inspeccionesAdd"
    ),
    path(
        route="basesList/",
        view=views.my_soap_base(),
        name="basesList"
    ),
    path(
        route="rutasList/",
        view=views.my_soap_ruta(),
        name="rutasList"
    ),
    path(
        route="vehiculosList/",
        view=views.my_soap_vehiculo(),
        name="vehiculosList"
    ),
    path(
        route="llantasList/",
        view=views.my_soap_llanta(),
        name="llantasList"
    ),
    path(
        route="tallerFormulario",
        view=views.tallerFormularioView.as_view(),
        name="tallerFormulario"
    ),
    path(
        route="usuarioFormulario",
        view=views.usuarioFormularioView.as_view(),
        name="usuarioFormulario"
    ),
    path(
        route="aplicacionFormulario",
        view=views.aplicacionFormularioView.as_view(),
        name="aplicacionFormulario"
    ),
    path(
        route="4umbrales",
        view=views.CuatroUmbralesView.as_view(),
        name="CuatroUmbrales"
    ),
    path(
        route="serialVehiculo",
        view=views.SerialVehiculoView.as_view(),
        name="SerialVehiculo"
    ),
    path(
        route="tireEyeView",
        view=views.TireEyeView.as_view(),
        name="TireEyeView"
    ),
    path(
        route="tireDetail/<int:pk>/",
        view=views.tireDetailView.as_view(),
        name="tireDetail"
    ),
    path(
        route="diagrama/<int:pk>/",
        view=views.diagramaView.as_view(),
        name="diagrama"
    ),
    path(
        route="tireDiagrama/<int:pk>",
        view=views.tireDiagramaView.as_view(),
        name="tireDiagrama"
    ),
    path(
        route="inspeccionLlanta/<int:pk>/",
        view=views.inspeccionLlantaView.as_view(),
        name="inspeccionLlanta"
    ),
    path(
        route="inspeccion-vehiculo/<int:pk>/",
        view=views.inspeccionVehiculo.as_view(),
        name="inspeccionVehiculo"
    ),
    path(
        route="reporteVehiculo/<int:pk>/<str:tipo>",
        view=views.reporteVehiculoView.as_view(),
        name="reporteVehiculo"
    ),
    path(
        route="reporteLlanta/<int:pk>/<int:llanta>/<int:eje>/<int:num_llanta>/<str:pulpo>",
        view=views.reporteLlantaView.as_view(),
        name="reporteLlanta"
    ),
    path(
        route="configuracionVehiculo/<int:pk>/",
        view=views.configuracionVehiculoView.as_view(),
        name="configuracionVehiculo"
    ),
    path(
        route="configuracionLlanta",
        view=views.configuracionLlantaView.as_view(),
        name="configuracionLlanta"
    ),
    path(
        route="almacen",
        view=views.almacenView.as_view(),
        name="almacen"
    ),
    path(
        route="carrito-stock",
        view=views.carritoStockView.as_view(),
        name="carritoStock"
    ),
    path(
        route="antesDesechar",
        view=views.antesDesecharView.as_view(),
        name="antesDesechar"
    ),
    path(
        route="antesRenovar",
        view=views.antesRenovarView.as_view(),
        name="antesRenovar"
    ),
    path(
        route="conRenovador",
        view=views.conRenovadorView.as_view(),
        name="conRenovador"
    ),
    path(
        route="desechoFinal",
        view=views.desechoFinalView.as_view(),
        name="desechoFinal"
    ),
    path(
        route="nueva",
        view=views.nuevaView.as_view(),
        name="nueva"
    ),
    path(
        route="renovada",
        view=views.renovadaView.as_view(),
        name="renovada"
    ),
    path(
        route="servicio",
        view=views.servicioView.as_view(),
        name="servicio"
    ),
    path(
        route="rodante",
        view=views.rodanteView.as_view(),
        name="rodante"
    ),
    path(
        route="procesoDesecho",
        view=views.procesoDesechoView.as_view(),
        name="procesoDesecho"
    ),
    path(
        route="ordenSalidaRen",
        view=views.ordenSalidaRenView.as_view(),
        name="ordenSalidaRen"
    ),
     path(
        route= 'ordenSalidaRenDef/', 
        view= views.ordenSalidaRenDef, 
        name='ordenSalidaRenDef'
    ),
    path(
        route="ordenEntrada",
        view=views.ordenEntradaView.as_view(),
        name="ordenEntrada"
    ),
    path(
        route="orden-entrada-taller/<int:pk>",
        view=views.ordenEntradaTallerView.as_view(),
        name="ordenEntradaTaller"
    ),
    path(
        route="orden-entrada-stock/<int:pk>",
        view=views.ordenEntradaStockView.as_view(),
        name="ordenEntradaStock"
    ),
    path(
        route="ordenLlanta/<int:pk>",
        view=views.ordenLlantaView.as_view(),
        name="ordenLlanta"
    ),
    path(
        route= 'ordenLlantaDef/<int:id>', 
        view= views.ordenLlantaDef, 
        name='ordenLlantaDef'
    ),
    path(
        route= 'ordenLlantaDeleteDef/<int:id>', 
        view= views.ordenLlantaDeleteDef, 
        name='ordenLlantaDeleteDef'
    ),
    path(
        route= 'redireccionOrden/<int:id>', 
        view= views.redireccionOrden, 
        name='redireccionOrden'
    ),
    path(
        route="tallerDestino",
        view=views.tallerDestinoView.as_view(),
        name="tallerDestino"
    ),
    path(
        route="stockDestino",
        view=views.stockDestinoView.as_view(),
        name="stockDestino"
    ),
    path(
        route="procesoRenovado",
        view=views.procesoRenovadoView.as_view(),
        name="procesoRenovado"
    ),
    path(
        route="vehicleList",
        view=views.vehicleListView.as_view(),
        name="vehicleList"
    ),
    path(
        route="taller/<int:pk>",
        view=views.planTallerView.as_view(),
        name="planTaller"
    ),
    path(
        route="calendario",
        view=views.calendarView.as_view(),
        name="calendario"
    ),
    path(
        route="webservices",
        view=views.webservicesView.as_view(),
        name="webservices"
    ),
     path(
        route="vistaordenes",
        view=views.vistaordenesView.as_view(),
        name="vistaordenes"
    ),
    path(
        route="formordennueva",
        view=views.formordennuevaView.as_view(),
        name="formordennueva"
    ),
    path(
        route="download1",
        view=views.download_rendimiento_de_llanta,
        name="download1"
    ),
    path(
        route="download2",
        view=views.download_reemplazo_estimado,
        name="download2"
    ),
    path(
        route="perdida-rendimiento",
        view=views.perdidaRendimientoView.as_view(),
        name="perdidaRendimiento"
    ),
    path(
        route="informe_de_perdida_y_rendimiento",
        view=views.informe_de_perdida_y_rendimiento,
        name="informe_de_perdida_y_rendimiento"
    ),
    path(
        route="OSEmingUEZRAftp_newpick",
        view=views.ftp_newpick,
        name="ftp_newpick"
    ),
    path(
        route="reporteInspeccion/<int:pk>/<str:tipo>",
        view=views.ReporteInspeccion.as_view(),
        name="reporteInspeccion"
    ),
    path(
        route="reporteEdicionLlanta/<int:pk>/<str:tipo>",
        view=views.reporteEdicionLlanta.as_view(),
        name="reporteEdicionLlanta"
    ),
    path(
        route="reporteEdicion/<int:pk>/<str:tipo>",
        view=views.ReporteEdicion.as_view(),
        name="reporteEdicion"
    ),
    path(
        route="historial-transacciones",
        view=views.historialTransacciones.as_view(),
        name="historialTransacciones"
    ),
    path(
        route="orden-desecho",
        view=views.reporteDesechoView.as_view(),
        name="ordenDesechoTemplete"
    ),
    path(
        route="historial-desecho",
        view=views.historialDesechoView.as_view(),
        name="ordenDesecho"
    ),
    path(
        route="download_todo",
        view=views.download_todo,
        name="download_todo"
    ),
    
    #----------------------APIS---------------------
    
    #-----------------------A-----------------------
    
    #-----------------------B-----------------------
    
    #-----------------------C-----------------------
    
    path(
        route="api/contextoapi",
        view=views_rest.ContextoApi.as_view(),
        name="contextoapi"
    ),

    path(
        route="api/carritollantasapi",
        view=views_rest.CarritoLlantasApi.as_view(),
        name="carritollantasapi"
    ),
    
    path(
        route="api/carritocountapi",
        view=views_rest.CarritoCountApi.as_view(),
        name="carritocountapi"
    ),
    
    #-----------------------D-----------------------
    
    #-----------------------E-----------------------
    
    #-----------------------F-----------------------
    
    #-----------------------G-----------------------
    
    path(
        route="api/generacionllantanueva",
        view=views_rest.GeneracionLlantaNuevaView.as_view(),
        name="generacionllantanueva"
    ),
    
    #-----------------------H-----------------------
    
    path(
        route="api/historicodeorden",
        view=views_rest.HistoricoDeOrdenApi.as_view(),
        name="historicodeorden"
    ),
    
    #-----------------------I-----------------------
    
    #-----------------------J-----------------------
    
    #-----------------------K-----------------------
    
    #-----------------------L-----------------------
    
    #-----------------------M-----------------------
    
    #-----------------------N-----------------------
    
     path(
        route="api/numtirestock",
        view=views_rest.NumTireStock.as_view(),
        name="numtirestock"
    ),
     
    #-----------------------Ñ-----------------------
    
    #-----------------------O-----------------------
    
    path(
        route="api/ordenllantanueva",
        view=views_rest.OrdenLlantaNuevaView.as_view(),
        name="ordenllantanueva"
    ),
    path(
        route="api/ordersearch",
        view=views_rest.OrderSearch.as_view(),
        name="ordersearch"
    ),
        path(
        route="api/opcionesdesecho",
        view=views_rest.OpcionesDesechoApi.as_view(),
        name="opcionesdesecho"
    ),
    #-----------------------P-----------------------

    path(
        route="api/panelrenovado",
        view=views_rest.PanelRenovadoApi.as_view(),
        name="panelrenovado"
    ),

    path(
        route="api/procesodesecho",
        view=views_rest.ProcesoDesechoApi.as_view(),
        name="procesodesecho"
    ),
    #-----------------------Q-----------------------

    #-----------------------R-----------------------

    #-----------------------S-----------------------

    #-----------------------T-----------------------

      path(
        route="api/tiresearch",
        view=views_rest.TireSearch.as_view(),
        name="tiresearch"
    ),
      path(
        route="api/tiresearchalmacen",
        view=views_rest.TireSearchAlmacen.as_view(),
        name="tiresearchalmacen"
    ),
    path(
        route="api/tiresearchtaller",
        view=views_rest.TireSearchTaller.as_view(),
        name="tiresearchtaller"
    ),

    #-----------------------U-----------------------

    #-----------------------V-----------------------
    
    path(
        route="api/vaciadocarrito",
        view=views_rest.VaciadoCarrito.as_view(),
        name="vaciadocarrito"
    ),

    #-----------------------W-----------------------

    #-----------------------X-----------------------

    #-----------------------Y-----------------------

    #-----------------------Z-----------------------


]