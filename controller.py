try:
    import numpy as np
    import random
    from PyQt5 import uic
    from PyQt5 import QtGui, QtWidgets, QtCore
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
    from scipy.special import jv as bessel
except ModuleNotFoundError:
    print("Module Not Found")

class Controller(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()

        # VIEW
        uic.loadUi("GUI.ui", self)

        # BUTTON GENERATE
        self.generate.clicked.connect(self.Angular_Modulation)
        
        # BUTTON CLEAR
        self.clear.clicked.connect(self.clear_view)

        # LABELS ESPECIALES
        self.labelresistance.setText("[Ω]")

    def Bessel_Function(self, m, R, Vc, fc, fm):

        bessel_list = []

        # Components
        for x in range(0, 10000):
            lateral = np.round(bessel(x, m), 2)

            if x > 0:
                if lateral == 0.0:
                    break
                else:
                    bessel_list.append(lateral)
            else:
                bessel_list.append(lateral)

        # Numpy Array
        new_bessel_list = np.array(bessel_list)

        # Voltage
        voltage_bessel_list = new_bessel_list * Vc

        # Average carrier power
        average_carrier_power = np.round((Vc**2)/(2*R), 3)

        # bessel power
        bessel_power = np.round(
            np.append((voltage_bessel_list[0]**2/(2*R)), voltage_bessel_list[1:]**2/R), 3)

        # Total power
        total_power = np.round(bessel_power.sum(), 3)

        # graph_power
        graph_power = np.append(
            voltage_bessel_list[:0:-1], voltage_bessel_list[1:])
        long = int(len(graph_power)/2)
        graph_power = np.insert(graph_power, long, voltage_bessel_list[0])

        # Frecuency
        frecuency = np.unique(np.append(np.array([x for x in range(
            fc, fc+1+fm*long, fm)]), np.array([x for x in range(fc, fc-1-fm*long, -fm)])))

        return [voltage_bessel_list, average_carrier_power, bessel_power, total_power, graph_power, frecuency, long, new_bessel_list]

    def Angular_Modulation(self):

        R = float(self.resistance.displayText().strip())
        Vc = float(self.voltagec.displayText().strip())
        Vm = float(self.voltagem.displayText().strip())
        fc = int(self.frecuencyc.displayText().strip())
        fm = int(self.frecuencym.displayText().strip())
        K = float(self.k.displayText().strip())
        K1 = float(self.k1.displayText().strip())

        # Deviation
        deviation_frecuency = np.round(K1*Vm,2)
        deviation_phase = np.round(K*Vm,2)

        # Modulation Value
        modulation_value_frecuency = np.round(deviation_frecuency/fm,2)
        modulation_value_phase = np.round(deviation_phase,2)

        # Modulation Percent
        m_frecuency = np.round((deviation_frecuency/(75*10**3))*100,2)

        # Bessel
        Bessel_frecuency = self.Bessel_Function(
            modulation_value_frecuency, R, Vc, fc, fm)
        Bessel_phase = self.Bessel_Function(
            modulation_value_phase, R, Vc, fc, fm)

        # Real BandWith
        RB_frecuency = 2*(Bessel_frecuency[6]*fm)
        RB_phase = 2*(Bessel_phase[6]*fm)

        # Minimun BandWith
        MB_frecuency = 2*(deviation_frecuency+fm)
        MB_phase = 2*(deviation_phase+fm)

        # Deviation ratio
        DR_frecuency = (75*10**3)/fm

        # GRAPHS
        self.modulating_graph_frecuency(Vm, fm)
        self.modulating_graph_phase(Vm, fm)
        self.carrier_graph(Vc, fc)
        self.modulated_graph_frecuency(Vc, fc, fm, modulation_value_frecuency)
        self.modulated_graph_phase(Vc, fc, fm, modulation_value_phase)
        self.spectre_graph_frecuency(
            Bessel_frecuency[4].tolist(), Bessel_frecuency[5])
        self.spectre_graph_phase(
            Bessel_phase[4].tolist(), Bessel_phase[5])

        # GENERAL INFORMATION
        self.general_information((K1, K), (deviation_frecuency, deviation_phase), (modulation_value_frecuency, modulation_value_phase), m_frecuency, (
            RB_frecuency, RB_phase), (MB_frecuency, MB_phase), DR_frecuency, (Bessel_frecuency[1], Bessel_phase[1]), (Bessel_frecuency[3], Bessel_phase[3]))

        # BESSEL INFORMATION
        self.bessel_information((Bessel_frecuency[7],Bessel_phase[7]),(Bessel_frecuency[0],Bessel_phase[0]),(Bessel_frecuency[2],Bessel_phase[2]))

    def general_information(self, SD, D, m, pm, RBW, MBW, DR, Pprom, Ptotal):

        self.table.setColumnCount(3)
        self.table.setRowCount(10)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setVisible(False)

        width = self.table.maximumWidth()/3
        height = self.table.maximumHeight()/10

        for x in range(0, 3):
            self.table.setColumnWidth(x, width)

        for y in range(0, 10):
            self.table.setRowHeight(y, height)

        # Rows Titles
        Values = ["VALUES", "DS", "Δf-Δθ", "m", "% m",
                  "RBW", "MBW", "DR", "P-MEAN-CARRIER", "P-TOTAL"]

        FM = ["FM", str(SD[0])+" [Hz/V]", str(D[0])+" [Hz]", str(m[0]), str(pm),
              str(RBW[0])+" [Hz]", str(MBW[0])+" [Hz]", str(DR), str(Pprom[0])+" [W]", str(Ptotal[0])+" [W]"]

        PM = ["PM", str(SD[1])+" [rad/V]", str(D[1])+" [rad]", str(m[1])+" [rad]", "-",
              str(RBW[1])+" [Hz]", str(RBW[1])+" [Hz]", "-", str(Pprom[1])+" [W]", str(Ptotal[1])+" [W]"]

        for x in range(0, len(Values)):
            self.table.setCellWidget(x, 0, QtWidgets.QLineEdit(
                text=Values[x], frame=False, alignment=QtCore.Qt.AlignCenter))
            self.table.setCellWidget(x, 1, QtWidgets.QLineEdit(
                text=FM[x],  frame=False, alignment=QtCore.Qt.AlignCenter))
            self.table.setCellWidget(x, 2, QtWidgets.QLineEdit(
                text=PM[x],  frame=False, alignment=QtCore.Qt.AlignCenter))


    def bessel_information(self,B,V,P):

        # Max Column Frecuency vs fase
        colmax = len(B[0]) if len(B[0])>=len(B[1]) else len(B[1])

        self.tableb.setColumnCount(colmax+1)
        self.tableb.setRowCount(8)
        self.tableb.verticalHeader().setVisible(False)
        self.tableb.horizontalHeader().setVisible(False)

        enum=[x for x in range(0,colmax)]
        values=[enum,B[0],V[0],P[0],enum,B[1],V[1],P[1]]
        titles=["FRECUENCY","Jn","Vn [V]","P [W]","PHASE","Jn","Vn [V]","P [W]"]
        
        for x in range(0,len(values)):
            self.tableb.setCellWidget(x, 0, QtWidgets.QLineEdit(text=titles[x], frame=False, alignment=QtCore.Qt.AlignCenter))
            for y in range(0,len(values[x])):
                self.tableb.setCellWidget(x, y+1, QtWidgets.QLineEdit(text=str(np.round(values[x][y],2)), frame=False, alignment=QtCore.Qt.AlignCenter))


    def modulating_graph_frecuency(self, Vm, fm):

        t = np.linspace(0, 0.0001, 1000)
        signal = Vm*np.sin(2*np.pi*fm*t)

        self.modulating.canvas.axes.clear()
        self.modulating.canvas.axes.plot(t, signal,'r')
        self.modulating.canvas.axes.set(
            xlabel='Time (s)', ylabel='Voltage (V)')
        self.modulating.canvas.axes.ticklabel_format(axis="both", style="sci", scilimits=(0,0))
        self.modulating.canvas.axes.set_title('Modulating Signal')
        self.modulating.canvas.axes.grid(True)
        self.modulating.canvas.draw()

    def modulating_graph_phase(self, Vm, fm):

        t = np.linspace(0, 0.0001, 1000)
        signal = Vm*np.cos(2*np.pi*fm*t)

        self.modulatingp.canvas.axes.clear()
        self.modulatingp.canvas.axes.plot(t, signal,'r')
        self.modulatingp.canvas.axes.set(
            xlabel='Time (s)', ylabel='Voltage (V)')
        self.modulatingp.canvas.axes.ticklabel_format(axis="both", style="sci", scilimits=(0,0))  
        self.modulatingp.canvas.axes.set_title('Modulating Signal')
        self.modulatingp.canvas.axes.grid(True)
        self.modulatingp.canvas.draw()

    def carrier_graph(self, Vc, fc):

        t = np.linspace(0, 0.0001, 1000)
        signal = Vc*np.cos(2*np.pi*fc*t)

        self.carrier.canvas.axes.clear()
        self.carrier.canvas.axes.plot(t, signal,'g')
        self.carrier.canvas.axes.set(xlabel='Time (s)', ylabel='Voltage (V)')
        self.carrier.canvas.axes.ticklabel_format(axis="both", style="sci", scilimits=(0,0))
        self.carrier.canvas.axes.set_title('Carrier Signal')
        self.carrier.canvas.axes.grid(True)
        self.carrier.canvas.draw()

        self.carrierp.canvas.axes.clear()
        self.carrierp.canvas.axes.plot(t, signal,'g')
        self.carrierp.canvas.axes.set(xlabel='Time (s)', ylabel='Voltage (V)')
        self.carrierp.canvas.axes.ticklabel_format(axis="both", style="sci", scilimits=(0,0))  
        self.carrierp.canvas.axes.set_title('Carrier Signal')
        self.carrierp.canvas.axes.grid(True)
        self.carrierp.canvas.draw()

    def modulated_graph_frecuency(self, Vc, fc, fm, m):

        t = np.linspace(0, 0.0001, 1000)
        signal = Vc*np.cos(2*np.pi*fc*t + m*np.sin(2*np.pi*fm*t))

        self.modulated.canvas.axes.clear()
        self.modulated.canvas.axes.plot(t, signal,'k')
        self.modulated.canvas.axes.set(
            xlabel='Time (s)', ylabel='Voltage (V)')
        self.modulated.canvas.axes.ticklabel_format(axis="both", style="sci", scilimits=(0,0)) 
        self.modulated.canvas.axes.set_title('Modulated Wave')
        self.modulated.canvas.axes.grid(True)
        self.modulated.canvas.draw()

    def modulated_graph_phase(self, Vc, fc, fm, m):

        t = np.linspace(0, 0.0001, 1000)
        signal = Vc*np.cos(2*np.pi*fc*t + m*np.cos(2*np.pi*fm*t))

        self.modulatedp.canvas.axes.clear()
        self.modulatedp.canvas.axes.plot(t, signal,'k')
        self.modulatedp.canvas.axes.set(
            xlabel='Time (s)', ylabel='Voltage (V)')
        self.modulatedp.canvas.axes.ticklabel_format(axis="both", style="sci", scilimits=(0,0)) 
        self.modulatedp.canvas.axes.set_title('Modulated Wave')
        self.modulatedp.canvas.axes.grid(True)
        self.modulatedp.canvas.draw()

    def spectre_graph_frecuency(self, V, f):

        self.frecuency.canvas.axes.clear()
        self.frecuency.canvas.axes.stem(f, V, 'm',markerfmt='bo',use_line_collection=True)
        self.frecuency.canvas.axes.set(
            xlabel='Frecueny (Hz)', ylabel='Voltage (V)')
        self.frecuency.canvas.axes.ticklabel_format(axis="both", style="sci", scilimits=(0,0)) 
        self.frecuency.canvas.axes.set_title('Spectrum')
        self.frecuency.canvas.axes.grid(True)
        self.frecuency.canvas.draw()

    def spectre_graph_phase(self, V, f):

        self.frecuencyp.canvas.axes.clear()
        self.frecuencyp.canvas.axes.stem(f, V,'m', markerfmt='bo', use_line_collection=True)
        self.frecuencyp.canvas.axes.set(
            xlabel='Frecuency (Hz)', ylabel='Voltage (V)')
        self.frecuencyp.canvas.axes.ticklabel_format(axis="both", style="sci", scilimits=(0,0)) 
        self.frecuencyp.canvas.axes.set_title('Spectrum')
        self.frecuencyp.canvas.axes.grid(True)
        self.frecuencyp.canvas.draw()

    def clear_view(self):

        # TABLES
        self.table.clear()
        self.tableb.clear()

        # GRAPHS
        self.modulating.canvas.axes.clear()
        self.modulating.canvas.draw()

        self.carrier.canvas.axes.clear()
        self.carrier.canvas.draw()
    
        self.modulated.canvas.axes.clear()
        self.modulated.canvas.draw()

        self.frecuency.canvas.axes.clear()
        self.frecuency.canvas.draw()

        self.modulatingp.canvas.axes.clear()
        self.modulatingp.canvas.draw()

        self.carrierp.canvas.axes.clear()
        self.carrierp.canvas.draw()

        self.modulatedp.canvas.axes.clear()
        self.modulatedp.canvas.draw()

        self.frecuencyp.canvas.axes.clear()
        self.frecuencyp.canvas.draw()

        # INPUTS
        self.resistance.clear()
        self.voltagec.clear()
        self.voltagem.clear()
        self.frecuencyc.clear()
        self.frecuencym.clear()
        self.k.clear()
        self.k1.clear()