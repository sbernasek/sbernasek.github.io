require 'rubygems'
require 'rake'
require 'rdoc'
require 'date'
require 'yaml'
require 'tmpdir'
require 'jekyll'
require 'shellwords'

system "git checkout source"
system "echo On source branch."

desc "Generate blog files"
task :generate do
  Jekyll::Site.new(Jekyll.configuration({
    "source"      => ".",
    "destination" => "./_site"
  })).process
  message = "Build completed at #{Time.now.utc}"
  system "echo #{message.shellescape}"
end

# desc "Generate and publish blog to gh-pages"
# task :publish => [:generate] do
#   Dir.mktmpdir do |tmp|
#     system "mv _site/* #{tmp}"
#     system "git checkout master"
#     system "rm -rf *"
#     system "mv #{tmp}/* ."
#     message = "Site updated at #{Time.now.utc}".shellescape
#     system "git add ."
#     system "git commit -am #{message}"
#     system "git push origin master --force"
#     system "git checkout source"
#     timestamp = "#{Time.now.utc}"
#     system "echo Deployment completed at #{timestamp.shellescape}."
#   end
# end

# task :default => :publish
