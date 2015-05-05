# Compass is a great cross-platform tool for compiling SASS. 
# This compass config file will allow you to 
# quickly dive right in.
# For more info about compass + SASS: http://net.tutsplus.com/tutorials/html-css-techniques/using-compass-and-sass-for-css-in-your-next-project/

environment = :production

#########
# 1. Set this to the root of your project when deployed:
http_path = "/"

# 2. probably don't need to touch these
static_dir = "icw/static"
css_dir = "#{static_dir}/css"
sass_dir = "#{css_dir}/scss"
images_dir = "#{static_dir}/img"
javascripts_dir = "#{static_dir}/js"
relative_assets = true

# 3. You can select your preferred output style here (can be overridden via the command line):
output_style = (environment == :production ? :compressed : :expanded)

# To disable debugging comments that display the original location of your selectors. Uncomment:
line_comments = (environment == :production ? false : true)

# don't touch this
preferred_syntax = :scss
