import math
from dataclasses import replace
import unittest
from motor_alertas import Fragmento, MotorAlertas


def f(n,valor=.2,llamada='ensayo',rev=1,t=None):
    return Fragmento(llamada,n,rev,valor,n*2,n*2+.5 if t is None else t)


class PruebasMotor(unittest.TestCase):
    def test_aviso_por_contexto_y_fragmento(self):
        m=MotorAlertas('ensayo')
        for k,v in enumerate([.3,.9,.9,1.4],1): m.consumir(f(k,v))
        self.assertEqual(m.primeras,{'F':8.5,'C':6.5})
        self.assertEqual(len(m.decisiones),8)

    def test_duplicado_no_cuenta_dos_veces(self):
        m=MotorAlertas('ensayo');x=f(1,2)
        m.consumir(x);antes=(dict(m.primeras),len(m.decisiones),list(m.historial))
        self.assertEqual(m.consumir(x),())
        self.assertEqual((m.primeras,len(m.decisiones),list(m.historial)),antes)

    def test_revision_no_reescribe_el_aviso(self):
        m=MotorAlertas('ensayo');m.consumir(f(1,2))
        self.assertEqual(m.consumir(f(1,-10,rev=2,t=20)),())
        self.assertEqual(m.primeras['F'],2.5)
        self.assertEqual(m.historial[0],2)
        self.assertEqual(m.eventos[-1]['tipo'],'revision_tardia')

    def test_salto_no_se_clasifica_como_audio_normal(self):
        m=MotorAlertas('ensayo')
        with self.assertRaisesRegex(ValueError,'secuencia'):m.consumir(f(2,5))
        self.assertEqual(len(m.decisiones),0)
        self.assertIsNone(m.primeras['F'])
        m.consumir(f(1));self.assertEqual(len(m.decisiones),2)

    def test_rechaza_datos_incoherentes(self):
        for x in (f(1,math.nan),f(1,t=1),f(1,llamada='otra'),f(1,rev=0)):
            with self.subTest(x=x):
                m=MotorAlertas('ensayo')
                with self.assertRaises(ValueError):m.consumir(x)
                self.assertEqual(len(m.decisiones),0)

    def test_aislamiento_entre_llamadas(self):
        a,b=MotorAlertas('ensayo'),MotorAlertas('otra')
        a.consumir(f(1,5));b.consumir(f(1,.1,llamada='otra'))
        self.assertIsNotNone(a.primeras['F']);self.assertIsNone(b.primeras['F'])

    def test_fallo_cierre_y_conflicto(self):
        m=MotorAlertas('ensayo');m.fallo('transcriptor no responde')
        self.assertEqual(m.estado,'sin_analisis')
        with self.assertRaisesRegex(ValueError,'sesión'):m.consumir(f(1))
        self.assertEqual(m.cerrar(),{'F':None,'C':None})
        with self.assertRaisesRegex(ValueError,'sesión'):m.consumir(f(1))
        m=MotorAlertas('ensayo');m.consumir(f(1))
        with self.assertRaisesRegex(ValueError,'conflicto'):m.consumir(f(1,valor=9))

    def test_memoria_acotada_y_reloj(self):
        m=MotorAlertas('ensayo')
        m.consumir(f(1,t=40))
        with self.assertRaisesRegex(ValueError,'reloj'):m.consumir(f(2,t=20))
        for i in range(2,8):m.consumir(f(i,t=40+i))
        self.assertEqual(len(m.historial),3)
        self.assertEqual(len(m.decisiones),14)


if __name__=='__main__':unittest.main(verbosity=2)
