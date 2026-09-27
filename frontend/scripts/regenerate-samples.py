# Regenerates the three sample chapter PDFs into this folder.
# Requires: pip install reportlab
# Run from this directory: python3 regenerate-samples.py

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors

styles = getSampleStyleSheet()

H1 = ParagraphStyle('H1', parent=styles['Heading1'], fontSize=17, spaceAfter=6, textColor=colors.HexColor('#111827'))
H2 = ParagraphStyle('H2', parent=styles['Heading2'], fontSize=12.5, spaceBefore=12, spaceAfter=5, textColor=colors.HexColor('#1f2937'))
BODY = ParagraphStyle('BODY', parent=styles['Normal'], fontSize=10.3, leading=15, spaceAfter=8)
EQ = ParagraphStyle('EQ', parent=styles['Normal'], fontSize=12, leading=18, spaceBefore=6, spaceAfter=10,
                    leftIndent=28, fontName='Helvetica-Bold', textColor=colors.HexColor('#1d4ed8'))
NOTE = ParagraphStyle('NOTE', parent=styles['Normal'], fontSize=9.6, leading=14, leftIndent=18,
                      spaceAfter=8, textColor=colors.HexColor('#374151'))
SUB = ParagraphStyle('SUB', parent=styles['Normal'], fontSize=10.5, spaceAfter=10,
                     textColor=colors.HexColor('#6b7280'))


def build(path, blocks):
    doc = SimpleDocTemplate(path, pagesize=letter,
                            leftMargin=0.95 * inch, rightMargin=0.95 * inch,
                            topMargin=0.85 * inch, bottomMargin=0.85 * inch)
    story = []
    for style, text in blocks:
        if style == 'SP':
            story.append(Spacer(1, 10))
        else:
            story.append(Paragraph(text, {'H1': H1, 'H2': H2, 'BODY': BODY,
                                          'EQ': EQ, 'NOTE': NOTE, 'SUB': SUB}[style]))
    doc.build(story)


# ----------------------------------------------------------------------------
# 1. CHEMISTRY  -- High school, 11th grade, Chemistry I / AP Chemistry
# ----------------------------------------------------------------------------

chem = [
    ('H1', 'Chapter 11 &nbsp;|&nbsp; Gases and the Gas Laws'),
    ('SUB', 'Chemistry I &middot; Unit 4: States of Matter &middot; Grade 11'),

    ('H2', '11.1 &nbsp; The Behavior of Gases'),
    ('BODY', 'A gas has no fixed shape and no fixed volume. Its particles move freely and independently, '
             'colliding with each other and with the walls of the container. Because those particles are so '
             'far apart relative to their size, a gas can be compressed into a much smaller space than a '
             'liquid or a solid. This is why the volume of a gas is not a property of the gas alone. It '
             'depends on the conditions the gas is held under.'),
    ('BODY', 'Four measurable quantities describe the state of any gas sample: pressure, volume, temperature, '
             'and the amount of gas in moles. If you know three of them, the fourth is determined. The '
             'relationship between them is the subject of this chapter.'),

    ('H2', '11.2 &nbsp; Pressure and Volume'),
    ('BODY', 'Robert Boyle observed in 1662 that when the temperature of a fixed amount of gas is held '
             'constant, increasing the pressure decreases the volume. The two quantities are inversely '
             'proportional. Doubling the pressure halves the volume. Reducing the pressure to one third '
             'triples the volume.'),
    ('EQ', 'P<sub>1</sub>V<sub>1</sub> = P<sub>2</sub>V<sub>2</sub>'),
    ('BODY', 'The physical picture is a piston in a sealed cylinder. Push the piston down and the same number '
             'of particles are confined to a smaller space, so they strike the walls more often and the '
             'pressure rises. Release the piston and the gas expands until the pressure inside matches the '
             'pressure outside.'),

    ('H2', '11.3 &nbsp; Temperature and Volume'),
    ('BODY', 'Jacques Charles found that when pressure is held constant, the volume of a gas is directly '
             'proportional to its absolute temperature. Heating a gas makes its particles move faster. Faster '
             'particles strike the walls harder and more often, and the gas pushes outward until it occupies '
             'more space.'),
    ('EQ', 'V<sub>1</sub> / T<sub>1</sub> = V<sub>2</sub> / T<sub>2</sub>'),
    ('NOTE', 'Temperature in every gas law must be expressed in kelvin. To convert, add 273.15 to a Celsius '
             'reading. Using Celsius directly will produce nonsense, including negative volumes.'),

    ('H2', '11.4 &nbsp; The Ideal Gas Law'),
    ('BODY', 'The separate observations of Boyle, Charles, and Avogadro combine into one equation that relates '
             'all four quantities at once. This is the ideal gas law, and it is the central result of the '
             'chapter.'),
    ('EQ', 'PV = nRT'),
    ('BODY', 'Here P is pressure, V is volume, n is the amount of gas in moles, T is the absolute temperature '
             'in kelvin, and R is the universal gas constant. When pressure is measured in kilopascals and '
             'volume in liters, R has the value 8.314 L&middot;kPa per mol&middot;K.'),
    ('BODY', 'Solving for volume gives the form used most often in laboratory work, because pressure and '
             'temperature are the two conditions an experimenter can adjust directly:'),
    ('EQ', 'V = nRT / P'),
    ('BODY', 'Read this equation as a statement about competition. Temperature pushes the volume up. Pressure '
             'pushes it down. The volume you actually observe is the result of the two effects working against '
             'each other. Raising the temperature and raising the pressure by matching proportions leaves the '
             'volume unchanged.'),

    ('H2', '11.5 &nbsp; Worked Example'),
    ('BODY', 'A sealed cylinder contains 1.00 mol of nitrogen gas. The pressure is set to 100 kPa and the '
             'temperature to 300 K. Find the volume.'),
    ('NOTE', 'V = nRT / P = (1.00)(8.314)(300) / 100 = 24.9 L'),
    ('BODY', 'Now suppose the experimenter needs the gas to occupy exactly 18.0 L. Several combinations of '
             'pressure and temperature will produce that volume. Lowering the temperature to 216 K at the same '
             'pressure would do it. So would raising the pressure to 138 kPa at the original temperature. '
             'There is no single correct answer, only a set of conditions that satisfy the equation.'),

    ('H2', '11.6 &nbsp; Limits of the Ideal Model'),
    ('BODY', 'The ideal gas law assumes gas particles have no volume of their own and exert no attractive '
             'forces on one another. Real gases follow it closely at ordinary pressures and temperatures well '
             'above their boiling points. The model breaks down at very high pressure, where particle volume '
             'stops being negligible, and at very low temperature, where attractive forces begin to matter.'),

    ('H2', 'Practice'),
    ('BODY', '1. A gas occupies 12.0 L at 250 kPa. What volume will it occupy at 150 kPa if temperature is '
             'unchanged?'),
    ('BODY', '2. A 2.00 mol sample is held at 400 K and 200 kPa. Calculate the volume.'),
    ('BODY', '3. An engineer needs 1.00 mol of gas to fill exactly 20.0 L. Find two different pairs of '
             'pressure and temperature that achieve this, and explain why more than one answer exists.'),
    ('BODY', '4. Explain, in terms of particle motion, why raising the temperature of a gas in a rigid sealed '
             'container raises the pressure rather than the volume.'),
]

build('./chemistry-gas-laws-grade11.pdf', chem)


# ----------------------------------------------------------------------------
# 2. BIOLOGY  -- College, 1st year, General Biology I
# ----------------------------------------------------------------------------

bio = [
    ('H1', 'Chapter 53 &nbsp;|&nbsp; Population Ecology'),
    ('SUB', 'General Biology I &middot; Unit 8: Ecology &middot; First-year undergraduate'),

    ('H2', '53.1 &nbsp; Describing a Population'),
    ('BODY', 'A population is a group of individuals of the same species living in the same area and capable of '
             'interbreeding. Population ecology asks a quantitative question about such a group: how does its '
             'size change over time, and what limits it?'),
    ('BODY', 'Population size is written as N. The rate of change of that size is written dN/dt, read as the '
             'change in N with respect to time. When dN/dt is positive the population is growing. When it is '
             'zero the population is stable.'),

    ('H2', '53.2 &nbsp; Exponential Growth'),
    ('BODY', 'A population in an environment with unlimited resources grows at a rate proportional to its own '
             'size. Each individual contributes to reproduction, so more individuals means faster growth. This '
             'produces the exponential growth model.'),
    ('EQ', 'dN/dt = rN'),
    ('BODY', 'The constant r is the intrinsic rate of increase, sometimes called the per capita growth rate. '
             'It is the difference between the per individual birth rate and the per individual death rate. '
             'A larger r produces a steeper curve.'),
    ('BODY', 'Exponential growth is real but temporary. Bacteria in fresh medium, or a species newly introduced '
             'to an island, will follow this curve for a time. No population follows it indefinitely, because '
             'no environment has unlimited resources.'),

    ('H2', '53.3 &nbsp; Carrying Capacity'),
    ('BODY', 'Every environment can support only a finite number of individuals. That maximum sustainable '
             'population size is the carrying capacity, written K. It is set by whatever resource runs out '
             'first, which may be food, water, nesting sites, or space itself.'),
    ('BODY', 'As N approaches K, competition intensifies. Birth rates fall, death rates rise, and growth slows. '
             'When N reaches K, births and deaths balance and dN/dt falls to zero.'),

    ('H2', '53.4 &nbsp; The Logistic Growth Model'),
    ('BODY', 'The logistic model modifies exponential growth by adding a term that shuts growth down as the '
             'population fills the available space. It is the central equation of this chapter.'),
    ('EQ', 'dN/dt = rN (1 &minus; N/K)'),
    ('BODY', 'The bracketed term is the key. When N is very small compared with K, the fraction N/K is close '
             'to zero, the bracket is close to one, and the equation behaves almost exactly like exponential '
             'growth. When N approaches K, the fraction approaches one, the bracket approaches zero, and growth '
             'stops. The result is an S shaped curve, often called a sigmoid curve.'),
    ('NOTE', 'The steepest growth occurs at N = K/2. This is the inflection point of the logistic curve, and '
             'it is where the population is adding individuals fastest in absolute terms.'),

    ('H2', '53.5 &nbsp; Reading the Two Parameters'),
    ('BODY', 'The two parameters control different features of the curve, and students routinely confuse them.'),
    ('BODY', 'The value of r controls how quickly the population reaches its ceiling. It changes the steepness '
             'of the rise but not the final level. A population with a high r climbs sharply and flattens early. '
             'A population with a low r climbs gently and may still be rising after many generations.'),
    ('BODY', 'The value of K controls where the curve flattens. It sets the ceiling itself. Changing K raises '
             'or lowers the plateau without changing how fast the population approaches it.'),
    ('BODY', 'A useful consequence follows. A population can reach a given size at a given time through very '
             'different combinations of these two parameters. A fast growing population with a low ceiling and '
             'a slower growing population with a high ceiling may pass through the same point.'),

    ('H2', '53.6 &nbsp; Worked Example'),
    ('BODY', 'A population of deer is introduced to a reserve. The starting population is 20 individuals. Field '
             'studies estimate r at 0.30 per year and K at 500 individuals.'),
    ('NOTE', 'At N = 20: dN/dt = 0.30 &times; 20 &times; (1 &minus; 20/500) = 5.76 deer per year.'),
    ('NOTE', 'At N = 250: dN/dt = 0.30 &times; 250 &times; (1 &minus; 250/500) = 37.5 deer per year.'),
    ('NOTE', 'At N = 480: dN/dt = 0.30 &times; 480 &times; (1 &minus; 480/500) = 5.76 deer per year.'),
    ('BODY', 'Notice that the growth rate is the same at 20 individuals and at 480 individuals, for entirely '
             'different reasons. Early on there are too few individuals reproducing. Late on there are too few '
             'resources remaining. The population grows fastest in the middle.'),

    ('H2', '53.7 &nbsp; Density Dependence'),
    ('BODY', 'Factors that limit a population more strongly as density rises are called density dependent. '
             'Competition, predation, disease transmission, and waste accumulation all fall into this category, '
             'and all are captured by the bracketed term in the logistic equation. Density independent factors, '
             'such as a sudden freeze or a flood, reduce population size regardless of how crowded the '
             'population was.'),

    ('H2', 'Practice'),
    ('BODY', '1. A population has r = 0.5 and K = 1000. Calculate dN/dt at N = 100, N = 500, and N = 900.'),
    ('BODY', '2. Two populations reach 400 individuals after 25 years. One has r = 0.2, the other r = 0.6. '
             'What must be true of their carrying capacities? Explain.'),
    ('BODY', '3. Sketch the logistic curve for r = 0.4 and K = 800 over 40 years starting from N = 10. Mark '
             'the inflection point.'),
    ('BODY', '4. Explain why raising r does not raise the eventual population size.'),
]

build('./biology-population-growth-college.pdf', bio)


# ----------------------------------------------------------------------------
# 3. MATH  -- High school, 10th grade, Algebra II
# ----------------------------------------------------------------------------

math = [
    ('H1', 'Chapter 7 &nbsp;|&nbsp; Exponential Functions and Compound Interest'),
    ('SUB', 'Algebra II &middot; Unit 3: Exponential and Logarithmic Models &middot; Grade 10'),

    ('H2', '7.1 &nbsp; Linear Growth and Exponential Growth'),
    ('BODY', 'A linear function adds the same amount in every time period. An exponential function multiplies '
             'by the same factor in every time period. This difference seems small at the start and becomes '
             'enormous over long spans, which is why exponential models are used for anything that grows on '
             'its own output: populations, infections, and money left to accumulate.'),
    ('BODY', 'A savings account is the cleanest example. Interest earned in one year is added to the balance, '
             'and the next year interest is earned on the larger balance. Each year the growth is larger than '
             'the year before, even though the rate never changes.'),

    ('H2', '7.2 &nbsp; The Compound Interest Formula'),
    ('BODY', 'For a principal amount P invested at an annual rate r, compounded n times per year for t years, '
             'the final amount A is given by:'),
    ('EQ', 'A = P (1 + r/n)<super>nt</super>'),
    ('BODY', 'The rate r is written as a decimal, so five percent is entered as 0.05. The exponent nt counts '
             'the total number of compounding periods over the whole investment.'),

    ('H2', '7.3 &nbsp; Annual Compounding'),
    ('BODY', 'When interest is compounded once per year, n equals 1 and the formula simplifies to the form '
             'used throughout this chapter:'),
    ('EQ', 'A = P (1 + r)<super>t</super>'),
    ('BODY', 'This is the version to reach for in problems that specify annual compounding or that do not '
             'specify a compounding frequency at all.'),

    ('H2', '7.4 &nbsp; How the Two Variables Behave'),
    ('BODY', 'Two quantities control the outcome: the rate r and the time t. They do not act the same way, and '
             'recognizing the difference is the main goal of this section.'),
    ('BODY', 'The rate sits inside the base. Changing it changes the multiplier applied in every single period, '
             'so its effect compounds on itself. Raising a rate from 4 percent to 8 percent does far more than '
             'double the final amount over a long span.'),
    ('BODY', 'Time sits in the exponent. Each additional year multiplies the balance by the base one more time. '
             'Early years add little in absolute terms because the balance is small. Later years add a great '
             'deal, because the same percentage is applied to a much larger number.'),
    ('NOTE', 'A useful estimate is the rule of 72. Dividing 72 by the interest rate as a percentage gives the '
             'approximate number of years required for the balance to double. At 6 percent, a balance doubles '
             'in roughly 12 years.'),

    ('H2', '7.5 &nbsp; Worked Example'),
    ('BODY', 'A student invests 1,000 dollars at an annual rate of 5 percent, compounded annually. Find the '
             'balance after 10 years and after 30 years.'),
    ('NOTE', 'After 10 years: A = 1000 (1.05)<super>10</super> = 1,628.89'),
    ('NOTE', 'After 30 years: A = 1000 (1.05)<super>30</super> = 4,321.94'),
    ('BODY', 'The first ten years added about 629 dollars. The last ten years of the thirty year span added '
             'roughly 1,665 dollars. The rate never changed. Only the size of the balance being multiplied '
             'changed.'),

    ('H2', '7.6 &nbsp; Reaching a Target'),
    ('BODY', 'Many problems ask the reverse question. Given a goal amount, what combination of rate and time '
             'will reach it? Because two variables appear, there is generally not one answer but a family of '
             'answers.'),
    ('BODY', 'Suppose the goal is to turn 1,000 dollars into 3,000 dollars. A rate of 8 percent reaches that '
             'goal in about 14 years. A rate of 4 percent reaches the same goal in about 28 years. A rate of '
             '11 percent reaches it in about 11 years. Each pairing satisfies the equation.'),
    ('BODY', 'This is the practical trade off behind most saving decisions. A higher return shortens the wait. '
             'A longer horizon lowers the return required.'),

    ('H2', '7.7 &nbsp; Exponential Decay'),
    ('BODY', 'When a quantity decreases by a fixed percentage each period, the same formula applies with a '
             'negative rate. A car losing 15 percent of its value each year is modelled by A = P(1 &minus; 0.15)'
             '<super>t</super>. The curve falls steeply at first and then flattens, approaching but never '
             'reaching zero.'),

    ('H2', 'Practice'),
    ('BODY', '1. Find the balance on 2,500 dollars invested at 6 percent compounded annually for 18 years.'),
    ('BODY', '2. How many years does 1,000 dollars at 7 percent take to exceed 2,000 dollars?'),
    ('BODY', '3. Find two different pairs of rate and time that turn 500 dollars into 2,000 dollars, and '
             'explain why more than one pair works.'),
    ('BODY', '4. Compare 5,000 dollars at 3 percent for 40 years with 5,000 dollars at 6 percent for 20 years. '
             'Which ends higher, and why is the answer not obvious from the numbers alone?'),
]

build('./math-compound-interest-grade10.pdf', math)

print('done')
