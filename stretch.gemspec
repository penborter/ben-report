# frozen_string_literal: true

Gem::Specification.new do |spec|
  spec.name          = "stretch"
  spec.version       = "0.1.0"
  spec.authors       = ["penborter"]
  spec.email         = ["benpo@outlook.com"]

  spec.summary       = "Stretch jekyll template."
  spec.homepage      = "https://penborter.com"
  spec.license       = "MIT"

  spec.files         = `git ls-files -z`.split("\x0").select { |f| f.match(%r!^(assets|_layouts|_includes|_sass|LICENSE|README|_config\.yml)!i) }

  spec.add_runtime_dependency "jekyll", "~> 4.2"
end
