"""Motor de referencia sobre puntajes: no recibe audio ni ejecuta modelos de IA."""
from collections import deque
from dataclasses import dataclass
import math

VERSION = '1.1.0'


@dataclass(frozen=True)
class Fragmento:
    llamada: str
    numero: int
    revision: int
    evidencia: float
    fin_audio_s: float
    disponible_s: float


class MotorAlertas:
    """Una instancia por llamada. Conserva la primera alerta y el historial de decisiones."""
    def __init__(self, llamada, umbral=1.15, pesos=(1.0, 0.7, 0.5)):
        if not llamada or not math.isfinite(umbral):
            raise ValueError('llamada o umbral inválido')
        if not pesos or any(not math.isfinite(w) or w<=0 for w in pesos):
            raise ValueError('pesos inválidos')
        self.llamada, self.umbral, self.pesos = llamada, umbral, tuple(pesos)
        self.historial = deque(maxlen=len(self.pesos))
        self.estado = 'analizando'
        self.fragmentos = {}
        self.decisiones = []
        self.eventos = []
        self.primeras = {'F': None, 'C': None}
        self.ultimo_fin = -math.inf
        self.ultimo_disponible = -math.inf

    def _error(self, motivo):
        self.eventos.append({'tipo': 'rechazo', 'motivo': motivo})
        raise ValueError(motivo)

    def consumir(self, f):
        if self.estado != 'analizando':
            self._error('sesión no disponible')
        if f.llamada != self.llamada:
            self._error('identificador de otra llamada')
        if not isinstance(f.numero,int) or isinstance(f.numero,bool) or f.numero<1:
            self._error('número de fragmento inválido')
        if not isinstance(f.revision,int) or isinstance(f.revision,bool) or f.revision<1:
            self._error('revisión inválida')
        if any(not isinstance(v,(int,float)) or isinstance(v,bool) or not math.isfinite(v)
               for v in (f.evidencia,f.fin_audio_s,f.disponible_s)):
            self._error('valor no finito')
        if f.fin_audio_s<0 or f.disponible_s<f.fin_audio_s:
            self._error('tiempos incoherentes')
        previo=self.fragmentos.get(f.numero)
        if previo is not None:
            if f==previo:
                self.eventos.append({'tipo':'duplicado','numero':f.numero})
                return ()
            if f.revision>previo.revision and f.fin_audio_s==previo.fin_audio_s:
                self.eventos.append({'tipo':'revision_tardia','numero':f.numero,'revision':f.revision,
                                     'evidencia_revisada':f.evidencia,'disponible_s':f.disponible_s})
                return ()
            self._error('fragmento confirmado en conflicto')
        if f.numero!=len(self.fragmentos)+1:
            self._error('secuencia incompleta o desordenada')
        if f.fin_audio_s<=self.ultimo_fin or f.disponible_s<self.ultimo_disponible:
            self._error('reloj no monotónico')
        self.historial.append(f.evidencia)
        reciente=list(reversed(self.historial))
        w=self.pesos[:len(reciente)]
        c=sum(a*b for a,b in zip(reciente,w))/math.sqrt(sum(a*a for a in w))
        decisiones=[]
        for regla,puntaje in (('F',f.evidencia),('C',c)):
            cruza=puntaje>=self.umbral
            primera=cruza and self.primeras[regla] is None
            decision={
                'llamada':self.llamada,'numero':f.numero,'revision':f.revision,
                'regla':regla,'puntaje':puntaje,'umbral':self.umbral,
                'fin_audio_s':f.fin_audio_s,'decision_s':f.disponible_s,
                'cruza_umbral':cruza,'primera_alerta':primera,'version_motor':VERSION,
            }
            if primera:
                self.primeras[regla]=round(f.disponible_s,10)
            self.decisiones.append(decision)
            decisiones.append(decision)
        self.fragmentos[f.numero]=f
        self.ultimo_fin,self.ultimo_disponible=f.fin_audio_s,f.disponible_s
        return tuple(decisiones)

    def fallo(self,motivo):
        if self.estado!='analizando':
            self._error('sesión no disponible')
        self.estado='sin_analisis'
        self.eventos.append({'tipo':'fallo','motivo':str(motivo)})

    def cerrar(self):
        self.estado='cerrada'
        return dict(self.primeras)
