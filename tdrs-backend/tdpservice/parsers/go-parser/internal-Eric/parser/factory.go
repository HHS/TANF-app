package parser

func NewParser(programType ProgramType, isProgramAudit bool) *Parser {
	switch programType {
	case TANF, TRIBAL, SSP:
		if isProgramAudit {
			return nil
		}
		return nil
	case FRA:
		return nil
	default:
		return nil
	}
}
