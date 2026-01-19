class CodigosKPI:
    HEADCOUNT = 'HEADCOUNT'
    AUSENTISMO = 'AUSENTISMO'
    PUNTUALIDAD = 'PUNTUALIDAD'
    SALARIO_PROM = 'SALARIO_PROM'
    COSTO_NOMINA = 'COSTO_NOMINA'
    SOLICITUDES_PEND = 'SOLICITUDES_PEND'
    TOTAL_CARGOS = 'TOTAL_CARGOS'

    MANUAL = 'MANUAL' 
    
    OPCIONES = [
        (HEADCOUNT, 'Total Empleados'),
        (AUSENTISMO, 'Ausentismo Laboral'),
        (PUNTUALIDAD, 'Puntualidad'),
        (SALARIO_PROM, 'Salario Promedio'),
        (COSTO_NOMINA, 'Costo Nómina Total'),
        (SOLICITUDES_PEND, 'Solicitudes Pendientes'),
        (TOTAL_CARGOS, 'Cargos Definidos'),
        (MANUAL, 'Ingreso Manual'),
    ]