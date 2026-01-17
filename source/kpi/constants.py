class CodigosKPI:
    HEADCOUNT = 'HEADCOUNT'
    AUSENTISMO = 'AUSENTISMO'
    PUNTUALIDAD = 'PUNTUALIDAD'
    ROTACION = 'ROTACION'
    SALARIO_PROM = 'SALARIO_PROM'
    MANUAL = 'MANUAL' # Para KPIs que el usuario llena a mano
    
    OPCIONES = [
        (HEADCOUNT, 'Total Empleados'),
        (AUSENTISMO, 'Ausentismo Laboral'),
        (PUNTUALIDAD, 'Puntualidad'),
        (ROTACION, 'Rotación de Personal'),
        (SALARIO_PROM, 'Salario Promedio'),
        (MANUAL, 'Ingreso Manual'),
    ]