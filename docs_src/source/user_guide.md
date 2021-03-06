# User Guide

A general overview of the motivation for and functionality of Plot Curve, as implemented in
**seeq-plot-curve** is provided in this section.

## The Problem

When working with time series data, it is very common to want to create a new signal based on a relationship or function with 
an existing signal.  When the  formula for the calculation is simple and known, it can be directly input into Seeq 
via the formula editor.  But many relationships are empirical in nature, represented by data points which describe the 
relationship between variables.  

Some examples may include :

- Equipment Curves 
  - A [pump curve](https://www.pumpsandsystems.com/understanding-pump-curves) providing the relationships between flow, head, efficiency, etc
  - A [valve curve](https://www.industrialcontrolsonline.com/training/online/controlling-flow-ball-valves) describing the relationship between the flow coefficient of a valve and its opening percentage
- Experimental Data
  - Product properties (i.e. blend ratio properties, property estimation)
  - Physical effects of additives (i.e. [drag reducing agents](https://pdfs.semanticscholar.org/2353/62a58dbe58225041b237051a0c5bcf878879.pdf))
  
There also may be many unique curves that we wish to integrate into Seeq, and the units may (or may not) match the units 
of the input signal.  This process can be time-consuming and error-prone.

*Plot Curve* is a minimal tool to solve the problem of efficiently fitting tabular data with polynomial functions that can
be pushed to Seeq as formulas.  It allows for previewing of the functions and manual selection of the polynomial order.


## Usage

<iframe width="900" height="500" src="_static/plot-curve-demo.mp4" frameborder="0" allowfullscreen></iframe>
<br/><br/>

### Step 1 - Select a File
- Add all relevant dataset signals to the trend view. Any time range is acceptable, but any dependent signals should
   be added to the trend view *before* launching the Plot Curve Application. 
- 
- From the Tools tab in Workbench, select Add On Tools followed by *PlotCurve*.  After a moment the tool will load, you 
   will be prompted to select the data to be plotted.  Some instructions are provided on this screen, indicating the 
   required file format, and [providing a link to supported units](https://seeq.atlassian.net/wiki/spaces/KB/pages/112761878/Units+of+Measure+UOM).
   *Units must be in a Seeq supported format to allow for proper conversion.* 

<table>
   <td>
      <img alt="image" src="_static/step_2.png" width="1000" height="400">
   </td>
</table>

### Step 2 - Select a Curve

Once a file has been selected, the plotting screen is loaded and the following *plot curve* variables can be adjusted :

- *Selected Curve* : This is the selected curve from column 1 of the input file as shown above.
- *Independent Variable* : This is which variable from the input file should be used as the 'x' axis variable.  The units
  of this variable must be compatible with the units of Seeq dependent signal.  See the animated gif for an example.
- *Dependent Variable* : This is which variable from the input file should be used as the 'y' axis variable.  The resulting
  Seeq signal will have units corresponding to this variable.
- *Equation Order* : This is the order of the polynomial equation to be used for the formula.

<table>
   <td>
      <img alt="image" src="_static/step_3.png" width="1000" height="400">
   </td>
</table>

### Step 3 - Push to Seeq

- After a reasonable equation has been fit to the data, the next step is to select a signal from Seeq that will be used
   to calculate the new predicted/dependent variable.  The output signal name should be a unique name signal name as it will be pushed to workbench.

- Finally, when we are happy with the signal names, and the curve, we can push the formula to Seeq.  After a few minutes,
   the new signal will appear in the active worksheet.  If we have provided signal names for multiple curves, then a dialog
   will ask us if we want to push all signals, or only the active curve.
<br/>
<table>
   <td>
      <img alt="image" src="_static/single_push.png">
   </td>
</table>
<br/>
<table>
   <td>
      <img alt="image" src="_static/multi_push.png">
   </td>
</table>






