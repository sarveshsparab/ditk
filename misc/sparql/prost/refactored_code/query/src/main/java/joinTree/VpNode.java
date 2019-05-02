package joinTree;

import java.util.Collections;

import org.apache.spark.sql.SQLContext;

import executor.Utils;

/*
 * A node of the JoinTree that refers to the Vertical Partitioning.
 */
public class VpNode extends Node {

	private final String tableName;

	/*
	 * The node contains a single triple pattern.
	 */
	public VpNode(final TriplePattern triplePattern, final String tableName) {
		super();
		this.tableName = tableName;
		this.triplePattern = triplePattern;
		tripleGroup = Collections.emptyList();
	}

	@Override
	public void computeNodeData(final SQLContext sqlContext) {

		if (tableName == null) {
			System.err.println("The predicate does not have a VP table: " + triplePattern.predicate);
			return;
		}

		final StringBuilder query = new StringBuilder("SELECT DISTINCT ");

		// SELECT
		if (triplePattern.subjectType == ElementType.VARIABLE && triplePattern.objectType == ElementType.VARIABLE) {
			query.append("s AS " + Utils.removeQuestionMark(triplePattern.subject) + ", o AS "
					+ Utils.removeQuestionMark(triplePattern.object) + " ");
		} else if (triplePattern.subjectType == ElementType.VARIABLE) {
			query.append("s AS " + Utils.removeQuestionMark(triplePattern.subject));
		} else if (triplePattern.objectType == ElementType.VARIABLE) {
			query.append("o AS " + Utils.removeQuestionMark(triplePattern.object));
		}

		// FROM
		query.append(" FROM ");
		query.append("vp_" + tableName);

		// WHERE
		if (triplePattern.objectType == ElementType.CONSTANT || triplePattern.subjectType == ElementType.CONSTANT) {
			query.append(" WHERE ");
		}
		if (triplePattern.objectType == ElementType.CONSTANT) {
			query.append(" o='" + triplePattern.object + "' ");
		}

		if (triplePattern.subjectType == ElementType.CONSTANT) {
			query.append(" s='" + triplePattern.subject + "' ");
		}

		// DEBUG
		System.out.println("DEBUG: Query -> " + query.toString());
		sparkNodeData = sqlContext.sql(query.toString());
	}

}