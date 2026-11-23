"""Contrasta el motor con las salidas publicadas de la simulación versión 1.0."""
from pathlib import Path
from collections import defaultdict
import csv,json,platform,unittest
from motor_alertas import Fragmento, MotorAlertas

ROOT=Path(__file__).resolve().parents[1]

def auditar():
    config=json.loads((ROOT/'protocolo/configuracion.json').read_text())
    with (ROOT/'datos/fragmentos_sinteticos.csv').open(encoding='utf-8',newline='') as f:
        fragmentos=list(csv.DictReader(f))
    with (ROOT/'datos/llamadas_sinteticas.csv').open(encoding='utf-8',newline='') as f:
        llamadas=list(csv.DictReader(f))
    por_llamada=defaultdict(list)
    for r in fragmentos:por_llamada[r['id_llamada']].append(r)
    divergencias=[];comparaciones=0;decisiones=0
    for llamada in llamadas:
        for campo,sufijo in [('evidencia_ref_sim','ref'),('evidencia_perturbada_sim','perturbada')]:
            m=MotorAlertas(llamada['id_llamada'],config['umbral_comun'],config['pesos_contexto'])
            for f in por_llamada[m.llamada]:
                fin=float(f['fin_fragmento_s'])
                m.consumir(Fragmento(m.llamada,int(f['indice']),1,float(f[campo]),fin,
                                    round(fin+float(f['latencia_simulada_s']),10)))
            decisiones+=len(m.decisiones)
            for regla,v in m.cerrar().items():
                ref=llamada[f'alerta_{regla}_{sufijo}_s'];ref=float(ref) if ref else None
                comparaciones+=1
                if v!=ref:divergencias.append([m.llamada,regla,sufijo,ref,v])
    resultado={
        'alcance':'verificacion_logica_sobre_puntajes_sinteticos_sin_audio',
        'version_motor':'1.1.0','python':platform.python_version(),
        'llamadas':len(llamadas),'fragmentos_por_entrada':len(fragmentos),
        'entradas':['referencia_sintetica','perturbada_sintetica'],
        'comparaciones_primer_aviso':comparaciones,'decisiones_registradas':decisiones,
        'divergencias':divergencias,
        'casos_logicos':8,
    }
    tests=unittest.defaultTestLoader.discover(str(ROOT/'codigo'),pattern='test_motor.py')
    reporte=unittest.TextTestRunner(verbosity=2).run(tests)
    resultado['pruebas_logicas_ejecutadas']=reporte.testsRun
    resultado['pruebas_logicas_correctas']=reporte.wasSuccessful()
    (ROOT/'resultados/verificacion_motor.json').write_text(json.dumps(resultado,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(resultado,ensure_ascii=False,indent=2))
    assert not divergencias and reporte.wasSuccessful()
    return resultado

if __name__=='__main__':auditar()
